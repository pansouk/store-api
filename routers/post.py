from typing import Any
from database import database, post_table as postTable, comment_table as commentTable
from fastapi import APIRouter, HTTPException, status
from models.post import Comment, CommentIn, UserPost, UserPostIn, UserPostWithComments

router = APIRouter()


async def find_post(post_id: int):
    query = postTable.select().where(postTable.c.id == post_id)
    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=status.HTTP_201_CREATED)
async def create_post(post: UserPostIn):
    data = post.model_dump()
    query = postTable.insert().values(data)
    last_record_id = await database.execute(query)
    return {
        **data,
        "id": last_record_id,
    }


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    query = postTable.select()
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentIn):
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    data = comment.model_dump()
    query = commentTable.insert().values(data)
    last_record_id = await database.execute(query)
    return {
        **data,
        "id": last_record_id,
    }


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    query = commentTable.select().where(commentTable.c.post_id == post_id)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
