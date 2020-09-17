from sqlalchemy.orm.collections import attribute_mapped_collection

from spendingtracker import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey(id))
    name = db.Column(db.String(50), nullable=False)

    children = db.relationship(
        "Category",
        cascade="all, delete-orphan",
        # many to one + adjacency list - remote_side
        # is required to reference the 'remote'
        # column in the join condition.
        backref=db.backref("parent", remote_side=id),
        collection_class=attribute_mapped_collection("name"),
    )
