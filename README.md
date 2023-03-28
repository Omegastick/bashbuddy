# bashbuddy

bashbuddy is an LLM hooked up to a Bash terminal. It's as dangerous as it sounds, but it's also a lot of fun. It's pretty much a proof of concept right now, so expect jank.

## WARNING

It's recommended to run bashbuddy in a VM. It's perfectly capable of running `rm -rf --no-preserve-root /` if you give it the right permissions, so run it as root on your main OS at your own risk.

## Installation

```
poetry install
```

Or

```
pip install -e .
```

You'll also need to put your OpenAI API key in the `OPENAI_API_KEY` environment variable.

## Usage

```
bashbuddy "<command>"
```

## Configuration

You can change the model used by setting the `BASHBUDDY_MODEL` environment variable or setting it in `~/.config/bashbuddy/config.toml`:

```toml
model = "gpt-4"  # defaults to gpt-3.5-turbo
```

## Example

````
$ bashbuddy "Make a new directory called 'test', then put 3 files in it, each containing a haiku. The file name should be the title of the poem."


> Entering new AgentExecutor chain...
Question: What is the task?
Thought: I need to create a new directory called 'test' and then create 3 files in it, each containing a haiku. The file name should be the title of the poem.
Action:
```

{
"action": "Bash",
"action_input": "mkdir test && cd test && touch 'Autumn Moon.txt' 'Cherry Blossoms.txt' 'Winter Frost.txt' && echo 'An autumn moon\nfloats among the clouds;\nA perfect evening!' > 'Autumn Moon.txt' && echo 'Cherry blossoms bloom,\nSoftly falling petals kiss\nThe ground goodbye, love.' > 'Cherry Blossoms.txt' && echo 'Winter solitude -\nin a world of one color\nthe sound of wind.' > 'Winter Frost.txt'"
}

```

Observation:
Thought:I have successfully created the 'test' directory and added 3 files with haikus in them.
Action:
```

{
"action": "Bash",
"action_input": "ls test"
}

```

Observation: ls: cannot access 'test': No such file or directory

Thought:I need to change the directory to the parent directory first before running the ls command.
Action:
```

{
"action": "Bash",
"action_input": "cd .. && ls test"
}

```


Observation: Autumn Moon.txt
Cherry Blossoms.txt
Winter Frost.txt

Thought:The 'test' directory has been successfully created and contains 3 files with haikus in them.
Final Answer: The 'test' directory has been successfully created and contains 3 files with haikus in them.

> Finished chain.
The 'test' directory has been successfully created and contains 3 files with haikus in them.

$ cat test/*
An autumn moon
floats among the clouds;
A perfect evening!
Cherry blossoms bloom,
Softly falling petals kiss
The ground goodbye, love.
Winter solitude -
in a world of one color
the sound of wind.
````
