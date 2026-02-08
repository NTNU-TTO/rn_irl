import pytest
from base import IRLAssessment, SerializerMixin

def test_getDate_format():
    assessment = IRLAssessment()
    date_str = assessment._getDate()
    # Should be in YYYY-MM-DD format
    parts = date_str.split('-')
    assert len(parts) == 3
    assert len(parts[0]) == 4  # Year
    assert len(parts[1]) == 2  # Month
    assert len(parts[2]) == 2  # Day

# Add more tests for other methods as needed
class DummyColumn:
    def __init__(self, name):
        self.name = name

class DummyTable:
    columns = [DummyColumn('field1'), DummyColumn('field2')]

class DummySerializer(SerializerMixin):
    __table__ = DummyTable()
    def __init__(self, data):
        super().__init__(data)

def test_serializer_as_dict():
    data = {'field1': 123, 'field2': 'abc'}
    obj = DummySerializer(data)
    d = obj.as_dict()
    assert d['field1'] == 123
    assert d['field2'] == 'abc'

def test_IRLAssessment_str_repr():
    assessment = IRLAssessment()
    assessment.project_no = 42
    assessment.project_name = 'TestProject'
    assert str(assessment) == '42 TestProject'
    assert repr(assessment) == '42 TestProject'
