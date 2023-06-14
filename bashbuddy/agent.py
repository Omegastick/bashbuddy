from typing import Type

from langchain.agents import AgentExecutor, BaseSingleActionAgent, Tool
from langchain.agents.chat.base import ChatAgent
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.chat_models import ChatOpenAI

from bashbuddy.config import load_config
from bashbuddy.tools.file_tree import FileTree
from bashbuddy.tools.persistent_bash import PersistentBash

SUFFIX = (
    "Remember to always use the exact characters `Final Answer` when responding. "
    "Remember to break the task down into short commands for easy debugging. "
    "Remember to escape newlines, quotes and apostrophes when filling out files."
    "Begin!"
)


def get_agent_class(model_name: str) -> Type[BaseSingleActionAgent]:
    if model_name.endswith("-0613"):
        return OpenAIFunctionsAgent
    return ChatAgent


def create_agent_executor(tools: list[Tool], model: str) -> AgentExecutor:
    llm = ChatOpenAI(model_name=model, temperature=0.0)  # type: ignore
    agent_class = get_agent_class(model)
    agent = agent_class.from_llm_and_tools(llm=llm, tools=tools, suffix=SUFFIX)
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
        file_tree_tool = Tool(
            name="FileTree",
            description=(
                'Generates a file tree of the given directory. Input should be a path to a directory (eg. "."), and '
                "the output will be a file tree of that directory."
            ),
            func=FileTree(bash).get,
        )
        executor = create_agent_executor(tools=[bash_tool, file_tree_tool], model=config.model)
        output = executor.run(command)

    return output
