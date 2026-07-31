from dotenv import load_dotenv
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from typing import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph import START
from langgraph.graph import END
import streamlit as st

load_dotenv()
model = ChatOpenAI(proxy_model_name='gpt-4o')

class BatsmanState(TypedDict):

    runs: int
    balls: int
    fours: int
    sixes: int

    sr: float
    bpb: float
    boundary_percent: float
    summary: str

def calculate_sr(state:BatsmanState):
    sr=(state['runs']/state['balls'])*100
    return{'sr':sr}

def calculate_bpb(state:BatsmanState):
    bpb = state['balls']/(state['fours'] + state['sixes'])

    return {'bpb': bpb}

def calculate_boudary_percent(state:BatsmanState):
    boundary_percent = (((state['fours'] * 4) + (state['sixes'] * 6))/state['runs'])*100

    return {'boundary_percent': boundary_percent}

def summary(state: BatsmanState):

    summary = f"""
Strike Rate - {state['sr']} \n
Balls per boundary - {state['bpb']} \n
Boundary percent - {state['boundary_percent']}
"""
    
    return {'summary': summary}


graph = StateGraph(BatsmanState)

graph.add_node('calculate_sr', calculate_sr)
graph.add_node('calculate_bpb', calculate_bpb)
graph.add_node('calculate_boudary_percent', calculate_boudary_percent)
graph.add_node('summary', summary)

# edges

graph.add_edge(START, 'calculate_sr')
graph.add_edge(START, 'calculate_bpb')
graph.add_edge(START, 'calculate_boudary_percent')

graph.add_edge('calculate_sr', 'summary')
graph.add_edge('calculate_bpb', 'summary')
graph.add_edge('calculate_boudary_percent', 'summary')

graph.add_edge('summary', END)

workflow = graph.compile()

initial_state={'runs':100,'balls':40,'fours':6,'sixes':8}
final_state=workflow.invoke(initial_state)
print(final_state)


print(final_state["summary"])

print(final_state["bpb"])
print(final_state["sr"])


st.set_page_config(
    page_title="Batsman Performance Analyzer",
    layout="centered"
)

st.title("🏏 Batsman Performance Analyzer")

st.markdown(
    "Enter batsman statistics and calculate performance metrics."
)


runs = st.number_input(
    "Runs",
    min_value=0,
    value=50
)

balls = st.number_input(
    "Balls Faced",
    min_value=1,
    value=30
)

col1, col2 = st.columns(2)

with col1:
    fours = st.number_input(
        "Fours",
        min_value=0,
        value=4
    )

with col2:
    sixes = st.number_input(
        "Sixes",
        min_value=0,
        value=2
    )


if st.button("Calculate Performance"):

    state = {
        "runs": runs,
        "balls": balls,
        "fours": fours,
        "sixes": sixes
    }

    state.update(calculate_sr(state))
    state.update(calculate_bpb(state))
    state.update(calculate_boudary_percent(state))
    state.update(summary(state))

    st.success("Calculation Completed")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Strike Rate",
            state["sr"]
        )

    with c2:
        st.metric(
            "Balls/Boundary",
            state["bpb"]
        )

    with c3:
        st.metric(
            "Boundary %",
            f"{state['boundary_percent']}%"
        )

    st.subheader("Summary")

    st.info(state["summary"])