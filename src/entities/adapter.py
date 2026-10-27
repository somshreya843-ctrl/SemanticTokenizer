from .record import EntityRecord


class RecordAdapter:
    """
    Converts provider-specific records into EntityRecord.
    During migration, this allows old and new providers to coexist.
    """

    @staticmethod
    def from_dataframe_row(row, columns):
        return EntityRecord(dict(zip(columns, row)))

    @staticmethod
    def from_dict(data):
        return EntityRecord(data)

    @staticmethod
    def passthrough(record):
        if isinstance(record, EntityRecord):
            return record
        return EntityRecord(record)