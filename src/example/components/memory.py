class Memory:
    """Singleton runtime store for variables, functions, and printed output."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.reset()
        return cls._instance

    def reset(self) -> None:
        # stack[0] is the global frame. Additional frames are function-local.
        self.stack: list[dict[str, dict[str, object]]] = [{}]
        self.functions: dict[str, object] = {}
        self.output: list[str] = []

    @property
    def _current_frame(self) -> dict[str, dict[str, object]]:
        return self.stack[-1]

    @property
    def _global_frame(self) -> dict[str, dict[str, object]]:
        return self.stack[0]

    def push_frame(self) -> None:
        self.stack.append({})

    def pop_frame(self) -> None:
        assert len(self.stack) > 1, "Cannot pop the global frame"
        self.stack.pop()

    def is_global_scope(self) -> bool:
        return len(self.stack) == 1

    def has_in_current_frame(self, name: str) -> bool:
        return name in self._current_frame

    def has(self, name: str) -> bool:
        return self._lookup_frame(name) is not None

    def set(self, name: str, value: object, data_type: object) -> None:
        frame = self._current_frame
        if name in frame and frame[name]["type"] != data_type:
            raise TypeError(
                f"Cannot reassign '{name}' from "
                f"{self._format_type(frame[name]['type'])} to {self._format_type(data_type)}"
            )
        frame[name] = {"value": value, "type": data_type}

    def get(self, name: str) -> object:
        frame = self._lookup_frame(name)
        if frame is None:
            raise NameError(f"'{name}' is not defined")
        return frame[name]["value"]

    def get_type(self, name: str) -> object:
        frame = self._lookup_frame(name)
        if frame is None:
            raise NameError(f"'{name}' is not defined")
        return frame[name]["type"]

    def define_function(self, name: str, function_stmt: object) -> None:
        if name in self.functions:
            raise NameError(f"Function '{name}' is already defined")
        self.functions[name] = function_stmt

    def get_function(self, name: str) -> object:
        if name not in self.functions:
            raise NameError(f"Function '{name}' is not defined")
        return self.functions[name]

    def write_output(self, value: object) -> None:
        text = str(value)
        self.output.append(text)
        print(value)

    def _lookup_frame(self, name: str) -> dict[str, dict[str, object]] | None:
        for frame in [self._current_frame, self._global_frame]:
            if name in frame:
                return frame
        return None

    @staticmethod
    def _format_type(data_type: object) -> str:
        if hasattr(data_type, "value"):
            return str(data_type.value)
        if hasattr(data_type, "__name__"):
            return data_type.__name__
        return str(data_type)

    def __repr__(self) -> str:
        lines = []
        for i, frame in enumerate(self.stack):
            label = "global" if i == 0 else f"frame {i}"
            lines.append(f"--- {label} ---")
            for name, data in frame.items():
                lines.append(
                    f"  {name}: {data['value']} ({self._format_type(data['type'])})"
                )
        if self.functions:
            lines.append("--- functions ---")
            for name, function_stmt in self.functions.items():
                lines.append(f"  {name}: {function_stmt}")
        if self.output:
            lines.append("--- output ---")
            lines.extend(f"  {line}" for line in self.output)
        return "\n".join(lines) if lines else "<empty>"


if __name__ == "__main__":
    mem = Memory()
    mem.reset()

    mem.set("x", 10, int)
    mem.set("msg", "hello", str)

    mem.push_frame()
    mem.set("a", 42, int)

    print(mem.get("a"))
    print(mem.get("x"))

    mem.set("x", 99, int)
    print(mem.get("x"))

    mem.pop_frame()

    print(mem.get("x"))
    print(mem)
