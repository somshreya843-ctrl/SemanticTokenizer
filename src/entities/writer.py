from pathlib import Path


class EntityWriter:

    def __init__(self, output_path: str, encoding: str = "utf-8"):

        self.output_path = Path(output_path)

        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self.file = open(
            self.output_path,
            "w",
            encoding=encoding,
        )

    def write(self, entity: str):

        self.file.write(entity + "\n")

    def close(self):

        self.file.close()