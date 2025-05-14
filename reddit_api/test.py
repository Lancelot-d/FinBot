from adapter.finbot_agent import FinBotAgent

if __name__ == "__main__":
    agent = FinBotAgent()
    output = agent.run("What is XEQT.TO and whats the price of it?")
    print(output)