# Placeholder for Tree-sitter logic
# In production, this would import tree_sitter and build the AST
class ContextBuilder:
    def __init__(self):
        pass
        
    def get_context(self, location, file_content) -> str:
        """
        Naive implementation: Grabs 10 lines before and after.
        Real implementation would use AST to grab full function scope.
        """
        lines = file_content.split("\n")
        start = max(0, location.start_line - 10)
        end = min(len(lines), location.end_line + 10)
        return "\n".join(lines[start:end])
