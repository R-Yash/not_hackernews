from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict
from sqlalchemy.orm import Session

from db import get_db
from models import Comment as CommentSchema, CommentCreate, CommentUpdate, CommentDB
from routers.auth import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])

def _build_tree(flat_comments: List[Dict]) -> List[CommentSchema]:
    comment_map = {c["id"]: {**c, "children": []} for c in flat_comments}
    roots = []
    for c in comment_map.values():
        pid = c["parent_id"]
        if pid and pid in comment_map:
            comment_map[pid]["children"].append(c)
        else:
            roots.append(c)
    return [CommentSchema(**c) for c in roots]

@router.get("/posts/{post_id}/comments", response_model=List[CommentSchema])
async def list_comments(post_id: int, db: Session = Depends(get_db)):
    rows = db.query(CommentDB).filter(CommentDB.post_id == post_id).all()
    flat = [
        {"id": c.id, "post_id": c.post_id, "text": c.text, "parent_id": c.parent_id, "author": c.author}
        for c in rows
    ]
    return _build_tree(flat)

@router.post("/posts/{post_id}/comments", response_model=CommentSchema, status_code=201)
async def create_comment(
    post_id: int,
    comment_in: CommentCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pid = comment_in.parent_id if comment_in.parent_id not in (None, 0) else None

    if pid is not None:
        parent = db.query(CommentDB).filter(CommentDB.id == pid).first()
        if not parent or parent.post_id != post_id:
            raise HTTPException(status_code=400, detail="Invalid parent_id")

    comment = CommentDB(
        post_id=post_id,
        text=comment_in.text,
        parent_id=pid,
        author=current_user
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommentSchema.model_validate(comment)


@router.put("/comments/{comment_id}", response_model=CommentSchema)
async def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    c = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    if c.author != current_user:
        raise HTTPException(status_code=403, detail="Not your comment")
    c.text = comment_in.text
    db.commit()
    return CommentSchema.model_validate(c)

@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    root = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not root:
        raise HTTPException(status_code=404, detail="Comment not found")
    if root.author != current_user:
        raise HTTPException(status_code=403, detail="Not your comment")

    def collect_descendants(c):
        ids = [c.id]
        for child in db.query(CommentDB).filter(CommentDB.parent_id == c.id).all():
            ids.extend(collect_descendants(child))
        return ids

    ids = collect_descendants(root)
    db.query(CommentDB).filter(CommentDB.id.in_(ids)).delete(synchronize_session=False)
    db.commit()