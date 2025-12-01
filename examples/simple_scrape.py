from dotenv import load_dotenv

from thordata_langchain_tools import ThordataScrapeTool

load_dotenv()


if __name__ == "__main__":
    tool = ThordataScrapeTool()

    result = tool.invoke(
        {
            "url": "https://www.thordata.com",
            "js_render": False,
            "output_format": "HTML",
        }
    )

    # For HTML output this will be a long string.
    # Print only the first 1000 characters to keep the console readable.
    if isinstance(result, str):
        print(result[:1000])
    else:
        print(result)