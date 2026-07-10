import pytest

from app.data.sql_executor import execute_filtered_query


def test_execute_filtered_query_rejects_unknown_filter():
    with pytest.raises(ValueError):
        execute_filtered_query("recipes", {"unknown": 1})
