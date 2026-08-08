# Import any dependencies needed to execute sql queries
from .sql_execution import QueryMixin


# Define a class called QueryBase
# Use inheritance to add methods
# for querying the employee_events database.
class QueryBase(QueryMixin):

    # Create a class attribute called `name`
    # set the attribute to an empty string
    name = ""

    # Define a `names` method that receives
    # no passed arguments
    def names(self):

        # Return an empty list
        return []


    # Define an `event_counts` method
    # that receives an `id` argument
    # This method should return a pandas dataframe
    def event_counts(self, id):

        query = f"""
        SELECT
            event_date,
            SUM(positive_events) AS positive_events,
            SUM(negative_events) AS negative_events
        FROM employee_events
        WHERE {self.name}_id = {id}
        GROUP BY event_date
        ORDER BY event_date
        """

        return self.pandas_query(query)



    # Define a `notes` method that receives an id argument
    # This function should return a pandas dataframe
    def notes(self, id):

        query = f"""
        SELECT
            note_date,
            note
        FROM notes
        WHERE {self.name}_id = {id}
        ORDER BY note_date
        """

        return self.pandas_query(query)