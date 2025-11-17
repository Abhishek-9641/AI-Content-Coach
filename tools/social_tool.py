from langchain.tools import Tool

def social_media_optimizer(content: str):
    hashtags = "#AI #ContentCreation #Growth"
    platforms = {
        "Twitter": f"{content[:250]}... {hashtags}",
        "LinkedIn": f"{content}\n\nFollow for more tips! {hashtags}",
        "Instagram": f"{content}\n🔥 Save for later! {hashtags}"
    }
    output = "\n\n".join([f"{k}: {v}" for k, v in platforms.items()])
    return output

# --------------------------
#  Wrap as a LangChain tool
# --------------------------
social_tool = Tool(
    name="SocialMediaOptimizer",
    func=social_media_optimizer,
    description="Optimizes content for different social platforms."
)
