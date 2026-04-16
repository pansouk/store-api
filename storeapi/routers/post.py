import logging
from typing import Any
from storeapi.database import (
    database,
    post_table as postTable,
    comment_table as commentTable,
)
from fastapi import APIRouter, HTTPException, status
from storeapi.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)


logger = logging.getLogger(__name__)

router = APIRouter()


async def find_post(post_id: int):
    logger.info(f"Findind post with ID: {post_id}")
    query = postTable.select().where(postTable.c.id == post_id)
    logger.debug(query)
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

    logger.info("Getting all posts")
    logger.debug(query)

    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentIn):
    post = await find_post(comment.post_id)
    if not post:
        logger.error(f"Post with id {comment.post_id} not found")
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
    logger.info(f"Getting comments on post with id {post_id}")
    query = commentTable.select().where(commentTable.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.info(f"Gettiing post with id: {post_id} and its comment(s).")
    post = await find_post(post_id)
    if not post:
        logger.error(f"Post with id: {post_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
