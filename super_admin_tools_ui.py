import streamlit as st
from streamlit import session_state as ss

import super_admin_tools as sat
import ui

def validate_sql():
    """
    Callback function to validate SQL query using super_admin_tools.

    Args:
        query (str): The SQL query to be validated.

    Returns:
        tuple: A tuple containing a boolean indicating validity and a message.
    """
    query = ss.sql_query
 
    valid, message = sat.validate_sql(query)
    ss.query_state = valid
    ss.query_error_message = message


def execute_query():
    """
    Callback function to execute SQL query using super_admin_tools.

    Args:
        query (str): The SQL query to be executed.

    Returns:
        list: The result of the query execution.
    """
    query = ss.sql_query
    state, retval = sat.direct_query(query)
    ss.query_ex_state = state
    ss.query_retval = retval
    ss.acknowledge_risks = False


# The action starts here.
dark_mode = (st.context.theme.type == 'dark')
ui.add_logo(dark_mode)

st.subheader("SuperAdmin Tools - Use With Extreme Caution And At Your Own Risk!")
st.text_area("Write your SQL query below. Press Ctrl+Enter to validate.",
             help="Enter your SQL query below:",
             on_change=validate_sql,
             key='sql_query')

# Ensure query state has a valid value.
assert(ss.get('query_state') in [True, False, None])

if ss.sql_query == "":

    ss.query_state = None

if ss.get('query_state') is None:
    st.warning("Query not validated yet.")

elif ss.query_state == False:

    st.error(ss.query_error_message)

else:
    st.success("Query is valid!")

acknowledge_disabled = (ss.get('query_state') is not True)

if acknowledge_disabled:

    if ss.get('acknowledge_risks'):

        ss.acknowledge_risks = False

st.checkbox("I understand the risks of executing raw SQL queries.",
            disabled=acknowledge_disabled,
            key='acknowledge_risks')
execute_disabled = acknowledge_disabled or not(ss.acknowledge_risks)
st.button("Execute Query", 
            key='execute_query_btn', 
            disabled=execute_disabled,
            on_click=execute_query)

if ss.get('query_ex_state') is not None:

    if ss.query_ex_state:

        st.success("Query executed successfully!")

    else:

        st.error(f"Query execution failed!")

    st.text_area("Query Result(s):", value=str(ss.query_retval), height=200)
    