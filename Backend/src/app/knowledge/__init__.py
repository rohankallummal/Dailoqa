"""The documentation knowledge store the DocQA capability answers from.

``Backend/knowledge-store`` is an Open Knowledge Format bundle converted from the MDX
documentation under ``Frontend/src/features/docs/content/langdocs``. ``bundle`` loads it
and splits pages into citable sections; ``search`` ranks those sections against a question.

The bundle is checked in and is now maintained by hand: the converter that produced it
has been removed, so a change to the source documentation does not reach the store on
its own.
"""
