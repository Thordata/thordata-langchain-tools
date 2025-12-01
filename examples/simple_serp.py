from dotenv import load_dotenv

from thordata_langchain_tools import ThordataSerpTool

load_dotenv()  # Load THORDATA_* tokens and keys from a local .env file


if __name__ == "__main__":
    tool = ThordataSerpTool()

    result = tool.invoke(
        {
            "query": "Thordata proxy network",
            "engine": "google",
            "num": 3,
        }
    )
    print(result)