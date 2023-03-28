from langchain.agents import AgentExecutor, Tool
from langchain.agents.chat.base import ChatAgent
from langchain.chat_models import ChatOpenAI

from bashbuddy.config import load_config
from bashbuddy.persistent_bash import PersistentBash

SUFFIX = (
    "Remember to always use the exact characters `Final Answer` when responding. "
    "Remember to break the task down into short commands for easy debugging. "
    "Remember to escape newlines, quotes and apostrophes when filling out files."
    "Begin!"
)


def create_agent_executor(tools: list[Tool], model: str) -> AgentExecutor:
    print(model)
    llm = ChatOpenAI(temperature=0, model=model)
    agent = ChatAgent.from_llm_and_tools(llm=llm, tools=tools, suffix=SUFFIX)
    executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

    return executor


def run_agent(command: str) -> str:
    config = load_config()

    with PersistentBash() as bash:
        bash_tool = Tool(
            name="Bash",
            description=(
                "Executes commands in a bash terminal. Input should be valid commands, and the output will be any "
                "output from running that command."
            ),
            func=bash.run,
        )
        executor = create_agent_executor(tools=[bash_tool], model=config.model)
        output = executor.run(command)

    return output
