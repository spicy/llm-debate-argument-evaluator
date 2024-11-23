from typing import Any, Dict, List

from utils.logger import logger

from visualization.observer import DebateTreeSubject, Observer

#NOTE This is class is not used anymore

class NodeExpansionHandler(Observer):
    def __init__(self, debate_tree_subject: DebateTreeSubject):
        self.debate_tree_subject = debate_tree_subject
        self.debate_tree_subject.attach(self)

    def update(self, subject):
        # This method is called when the debate tree is updated
        # We don't need to do anything here as we're not automatically expanding nodes
        pass

    async def expand_node(self, node_id: str, new_arguments: List[Dict[str, Any]]):
        logger.info(f"Expanding node: {node_id}")
        debate_tree = self.debate_tree_subject.debate_tree
        if node_id not in debate_tree:
            logger.warning(f"Node {node_id} not found in the debate tree")
            return

        for i, argument in enumerate(new_arguments):
            new_node_id = f"{node_id}_{i}"
            debate_tree[new_node_id] = {
                "id": new_node_id, # TEMP
                "argument": argument["argument"],
                "score": argument["score"],
                "parent": node_id,
            }

        self.debate_tree_subject.debate_tree = debate_tree
        logger.info(f"Node {node_id} expanded with {len(new_arguments)} new arguments")
