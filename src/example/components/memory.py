class Memory:

    def __init__(self) -> None:
        # Stack of frames. stack[0] is always the global frame.
        self.stack: list[dict] = [{}]

    @property
    def _current_frame(self) -> dict:
        return self.stack[-1]

    @property
    def _global_frame(self) -> dict:
        return self.stack[0]

    # ------------------------------------------------------------------
    # Frame management — called by the interpreter on function call/return
    # ------------------------------------------------------------------

    def push_frame(self) -> None:
        """Enter a new function scope."""
        self.stack.append({})

    def pop_frame(self) -> None:
        """Leave the current function scope."""
        assert len(self.stack) > 1, "Cannot pop the global frame"
        self.stack.pop()

    # ------------------------------------------------------------------
    # Variable access
    # ------------------------------------------------------------------

    def set(self, name: str, value: object, data_type: type) -> None:
        """Create or overwrite a variable in the current frame."""
        self._current_frame[name] = {"value": value, "type": data_type}

    def get(self, name: str) -> object:
        """
        Static (lexical) scoping: look in the current frame first,
        then fall back to the global frame. Intermediate call frames
        are intentionally skipped — functions only see their own locals
        and globals, never the caller's locals.
        """
        for frame in [self._current_frame, self._global_frame]:
            if name in frame:
                return frame[name]["value"]
        raise NameError(f"'{name}' is not defined")

    def get_type(self, name: str) -> type:
        for frame in [self._current_frame, self._global_frame]:
            if name in frame:
                return frame[name]["type"]
        raise NameError(f"'{name}' is not defined")

    def is_global_scope(self) -> bool:
        return len(self.stack) == 1

    # ------------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        lines = []
        for i, frame in enumerate(self.stack):
            label = "global" if i == 0 else f"frame {i}"
            lines.append(f"--- {label} ---")
            for name, data in frame.items():
                lines.append(f"  {name}: {data['value']} ({data['type'].__name__})")
        return "\n".join(lines) if lines else "<empty>"


if __name__ == "__main__":
    mem = Memory()

    # global scope
    mem.set("x", 10, int)
    mem.set("msg", "hello", str)

    # simulate a function call: foo(a=42)
    mem.push_frame()
    mem.set("a", 42, int)

    print(mem.get("a"))    # 42  — found in current frame
    print(mem.get("x"))    # 10  — falls back to global frame

    mem.set("x", 99, int)  # creates a LOCAL x — does NOT affect global x
    print(mem.get("x"))    # 99  — local shadows global

    mem.pop_frame()

    print(mem.get("x"))    # 10  — local frame gone, global x untouched
    print(mem)
