


from typing import Optional
from uuid import UUID, uuid1


class BaseBlock:
    def __init__(self) -> None:
        self.id = uuid1()

class Image(BaseBlock):
    def __init__(self, url: str) -> None:
        super().__init__()
        self.url: str = url    

class Text(BaseBlock):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text: str = text

class Header(Text):
    pass


class Page:
    def __init__(self, blocks: list[BaseBlock]):
        self.blocks: list[BaseBlock] = blocks

    def insert_block(self, block: BaseBlock, position: Optional[int] = None):
        if position:
            self.blocks.insert(position,block)
        else:
            self.blocks.append(block)

    def add_blocks(self, blocks: list[BaseBlock]):
        for block in blocks:
            self.blocks.append(block)

    def remove_block(self, block_id: UUID):
        for block in self.blocks:
            if block.id == block_id:
                self.blocks.remove(block)
            

    def change_position(self, block_id: UUID, positoin: int):
        pass