from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from db import get_db
from models import Post as PostSchema, PostCreate, PostDB, CommentDB, Vote
from routers.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])

# posts: List[Post] = []
# next_post_id: int = 1
# votes: dict[Tuple[str, int], int] = {}

# def _update_comment_counts() -> dict[int, int]:
#     """
#     Build a mapping from post_id -> count of comments (including replies).
#     """
#     counts: dict[int, int] = {}
#     for c in _comments:
#         counts[c["post_id"]] = counts.get(c["post_id"], 0) + 1
#     return counts


# def total_posts() -> int:
#     """Return total number of posts."""
#     return len(posts)


@router.get("/", response_model=List[PostSchema])
async def list_posts(skip: int = Query(0, ge=0),limit: int = Query(10, gt=0),db: Session = Depends(get_db)):
    counts = dict(
        db.query(CommentDB.post_id, func.count(CommentDB.id))
          .group_by(CommentDB.post_id)
          .all()
    )
    posts = db.query(PostDB).offset(skip).limit(limit).all()
    result = []
    for p in posts:
        pc = counts.get(p.id, 0)
        result.append(PostSchema.from_orm(p).copy(update={"comment_count": pc}))
    return result

@router.post("/", response_model=PostSchema, status_code=201)
async def create_post(post_in: PostCreate, current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
    post = PostDB(
        title=post_in.title,
        url=post_in.url,
        text=post_in.text,
        author=current_user,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return PostSchema.model_validate(post)


@router.post("/{post_id}/vote", response_model=PostSchema)
async def vote_post(post_id: int,vote: int = Query(..., ge=-1, le=1),current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    v = db.query(Vote).filter(Vote.username == current_user, Vote.post_id == post_id).first()
    old = v.value if v else 0
    if vote == old:
        raise HTTPException(status_code=400, detail="You have already cast this vote")

    post.points += (vote - old)
    if v:
        v.value = vote
    else:
        db.add(Vote(username=current_user, post_id=post_id, value=vote))
    db.commit()
    db.refresh(post)
    return PostSchema.from_orm(post).copy(update={"comment_count": post.comments and len(post.comments) or 0})


@router.get("/{post_id}", response_model=PostSchema)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    count = db.query(func.count(CommentDB.id)).filter(CommentDB.post_id == post_id).scalar()
    return PostSchema.from_orm(post).copy(update={"comment_count": count})