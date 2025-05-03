from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Literal
from sqlalchemy.orm import Session
from sqlalchemy import func

from db import get_db
from models import Post as PostSchema, PostCreate, PostDB, CommentDB, Vote
from routers.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/", response_model=List[PostSchema])
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    sort: Literal["new", "top"] = Query("new", description="‘new’ → newest first; ‘top’ → highest votes first"),
    search: Optional[str] = Query(None, description="search term to match in post titles"),
    db: Session = Depends(get_db)
):
    """
    Lists posts with pagination, sorting, and title search.

    Args:
        skip: Number of posts to skip (for pagination).
        limit: Maximum number of posts to return.
        sort: Sorting criteria ('new' by creation time or 'top' by points).
        search: Optional search term to filter posts by title.
        db: The database session dependency.

    Returns:
        A list of PostSchema objects matching the criteria.
    """
    q = db.query(PostDB)

    if search:
        q = q.filter(PostDB.title.ilike(f"%{search}%"))

    if sort == "new":
        q = q.order_by(PostDB.id.desc())
    else: 
        q = q.order_by(PostDB.points.desc())

    posts = q.offset(skip).limit(limit).all()

    counts = dict(
        db.query(CommentDB.post_id, func.count(CommentDB.id))
          .group_by(CommentDB.post_id)
          .all()
    )

    result = []
    for p in posts:
        pc = counts.get(p.id, 0)
        result.append(PostSchema.from_orm(p).copy(update={"comment_count": pc}))

    return result

@router.post("/", response_model=PostSchema, status_code=201)
async def create_post(post_in: PostCreate, current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
    """
    Creates a new post authored by the current authenticated user.

    Args:
        post_in: The data for the new post (title, url, text). Author is ignored.
        current_user: The username of the authenticated user.
        db: The database session dependency.

    Returns:
        The newly created PostSchema object.
    """
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
    """
    Casts or updates a vote on a specific post by the current user.

    Args:
        post_id: The ID of the post to vote on.
        vote: The vote value (1, -1, or 0).
        current_user: The username of the authenticated user.
        db: The database session dependency.

    Raises:
        HTTPException: 404 Not Found if the post does not exist.
        HTTPException: 400 Bad Request if the user tries to cast the same vote value again.

    Returns:
        The updated PostSchema object with the new point total and comment count.
    """
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
    """
    Retrieves a single post by its ID, including its comment count.

    Args:
        post_id: The ID of the post to retrieve.
        db: The database session dependency.

    Raises:
        HTTPException: 404 Not Found if the post does not exist.

    Returns:
        The PostSchema object for the requested post.
    """
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    count = db.query(func.count(CommentDB.id)).filter(CommentDB.post_id == post_id).scalar()
    return PostSchema.from_orm(post).copy(update={"comment_count": count})