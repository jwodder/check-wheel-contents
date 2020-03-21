import attr

@attr.s
class Directory:
    subdirectories = attr.ib(factory=dict)
    files = attr.ib(factory=list)

    def __bool__(self):
        return bool(self.files or self.subdirectories)

    def add_at_path(self, file, pathparts):
        p, *parts = pathparts
        if not parts:
            self.files.append(file)
        else:
            self.subdirectories.setdefault(p, Directory())\
                               .add_at_path(file, parts)

    def all_files(self):
        yield from self.files
        for sd in self.subdirectories.values():
            yield from sd.all_files()
