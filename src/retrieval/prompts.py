"""
Experimental prompt templates for RAG system.

This module implements different prompt engineering strategies to compare
their effectiveness in preventing hallucinations and improving answer quality.

Strategies implemented:
1. Basic: Simple, direct prompting
2. Few-shot: Includes examples of good answers
3. Chain-of-thought: Encourages step-by-step reasoning
4. Anti-hallucination: Strict constraints to prevent hallucinations
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder



BASIC_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Use the following context to answer the user's question.
If you cannot find the answer in the context, say so clearly.
You can reference previous conversation when relevant.

Context:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
])


# Strategy 2: Few-shot Examples
FEW_SHOT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Use the following context to answer the user's question.

Here are examples of good answers:

Example 1:
Question: "What is the maximum takeoff weight?"
Context: "The aircraft has a maximum takeoff weight of 2,550 lbs as specified in Section 2.3"
Good Answer: "According to Section 2.3, the maximum takeoff weight is 2,550 lbs."

Example 2:
Question: "How do I start the engine?"
Context: [No relevant information about engine starting procedures]
Good Answer: "I cannot find information about engine starting procedures in the provided context."

Example 3:
Question: "What was the cruising speed mentioned earlier?"
Context: "Standard cruising speed is 122 knots"
Previous conversation: User asked about fuel capacity
Good Answer: "Earlier in our conversation, we discussed fuel capacity. Regarding your current question, the standard cruising speed is 122 knots according to the context."

Now answer the user's question using the context below:

Context:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
])


# Strategy 3: Chain-of-thought Reasoning
CHAIN_OF_THOUGHT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Answer questions using step-by-step reasoning.

Follow this process:
1. First, analyze what the question is asking
2. Search the context for relevant information
3. If found, explain the reasoning before giving the answer
4. If not found, clearly state what information is missing

Context:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
])


# Strategy 4: Anti-hallucination (Strict)
ANTI_HALLUCINATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a precise technical assistant. Follow these strict rules:

CRITICAL RULES:
1. ONLY use information explicitly stated in the context below
2. NEVER infer, assume, or add information not in the context
3. If the answer is not in the context, respond with: "This information is not available in the provided documents"
4. When answering, quote the relevant section from the context
5. If the context is ambiguous or unclear, state that explicitly
6. For conversational questions referencing previous answers, check the chat history

Context:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
])

# Strategy 5: Tree of Thoughts (ToT)
TREE_OF_THOUGHTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a precise assistant for aircraft manuals. Use Tree of Thoughts to solve the question:

Process:
1. Generate 3 possible reasoning paths (branches) based on the context.
2. For each path: Analyze the question, extract relevant info from context, reason step-by-step.
3. Evaluate each path: Which is most accurate and complete? Discard if it hallucinates or lacks evidence.
4. Select the best path and provide the final answer, quoting context.

If no path works, say "Information not available."

Context:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
])


# Strategy 6: Self-Consistency
SELF_CONSISTENCY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Use Self-Consistency:

1. Generate 3 independent reasoning chains for the question using the context.
2. For each: Step-by-step analysis, only using explicit context info.
3. Compare the 3 chains: Select the most consistent answer (majority vote if numerical; most supported if textual).
4. If inconsistent or not in context, state clearly.

Context:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
])


# Strategy 7: ReAct (Reason + Act)
REACT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a technical assistant. Use ReAct format: Thought -> Action -> Observation -> Final Answer.

- Thought: Reason about the question and plan next action.
- Action: e.g., "Search context for [key term]" or "Check history for reference".
- Observation: Note what you find (must be from context/history only).
- Repeat until ready, then give Final Answer.

End with "Final Answer: [response]". No hallucinations.

Context:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
])


# Strategy 8: Least-to-Most
LEAST_TO_MOST_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert in aviation manuals. Use Least-to-Most prompting:

1. Break the question into smaller sub-questions, from simple to complex.
2. Answer each sub-question using only the context, building on previous answers.
3. Combine into a final comprehensive response.
4. If any sub-question can't be answered from context, stop and say so.

Example breakdown for "How to troubleshoot engine failure?": 
- Sub1: What are common engine symptoms? 
- Sub2: What checks to perform? 
- Sub3: Repair steps.

Context:
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
])


# Updated Dictionary
PROMPT_STRATEGIES = {
    "basic": BASIC_PROMPT,
    "few-shot": FEW_SHOT_PROMPT,
    "chain-of-thought": CHAIN_OF_THOUGHT_PROMPT,
    "anti-hallucination": ANTI_HALLUCINATION_PROMPT,
    "tree-of-thoughts": TREE_OF_THOUGHTS_PROMPT,
    "self-consistency": SELF_CONSISTENCY_PROMPT,
    "react": REACT_PROMPT,
    "least-to-most": LEAST_TO_MOST_PROMPT
}


def get_prompt(strategy: str = "basic") -> ChatPromptTemplate:
    """
    Get a prompt template by strategy name.

    Args:
        strategy: One of "basic", "few-shot", "chain-of-thought", "anti-hallucination"

    Returns:
        ChatPromptTemplate for the specified strategy

    Raises:
        ValueError: If strategy is not recognized
    """
    if strategy not in PROMPT_STRATEGIES:
        raise ValueError(
            f"Unknown strategy '{strategy}'. "
            f"Valid options: {list(PROMPT_STRATEGIES.keys())}"
        )
    return PROMPT_STRATEGIES[strategy]
