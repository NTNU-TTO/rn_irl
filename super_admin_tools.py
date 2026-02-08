from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
import streamlit as st

Base = declarative_base()

def direct_query(query):
    """
    Executes a direct database query.

    Args:
        query (str): The SQL query to be executed.

    Returns:
        list: The result of the query execution.
    """
    engine = create_engine(st.secrets.db_details.db_path)
    state = None
    retval = None
    keyword = query.split()[0].upper()
 
    with engine.connect() as conn:

        try:

            result = conn.execute(text(query))
            state = True

            if keyword in ("SELECT", "SHOW", "PRAGMA", "DESCRIBE"):

                retval = result.fetchall()
            
            else:

                retval = f"Query executed successfully. {result.rowcount} rows affected."

            conn.commit()
        
        except Exception as e:

            state = False
            retval =  f"Error executing query:  \n{e}"
 
        finally:

            engine.dispose()

    return (state, retval)


def validate_sql(query):
    """
    Validates the SQL query to prevent harmful operations.

    Args:
        query (str): The SQL query to be validated.

    Raises:
        ValueError: If the query contains harmful operations.
    """
    harmful_statements = ['DROP', 'DELETE', 'ALTER', 'TRUNCATE']
    message = ""
    valid = True

    for statement in harmful_statements:

        if statement in query.upper():

            message += f"WARNING: Harmful SQL operation detected:  \n{statement}  \n"
    
    engine = create_engine(st.secrets.db_details.db_path)
 
    with engine.connect() as conn:

        try:

            conn.execute(text("EXPLAIN " + query))
            message = "Query is valid - you're good to go!"

        except Exception as e:

            valid = False
            message = f"Sorry, your query is not valid:  \n{e}"

        finally:

            engine.dispose()

    return (valid, message)