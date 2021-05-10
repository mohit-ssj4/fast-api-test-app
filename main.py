import database
import models
import schemas
import uvicorn
from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session

# This is used to create the table in the database
models.database.Base.metadata.create_all(bind=database.engine)

# This is used to instantiate the fastAPI application
app = FastAPI()

"""
This method is used to get the db session

:return db: database.SessionLocal()
"""

async def get_db():
    db = database.SessionLocal()

    try:
        yield db
    finally:
        db.close()

"""
This method is used to create ans insert a blog into the database

:param request: schemas.Blog
:param db: Session
:return object
"""

@app.post('/blog', tags=['Blog'], status_code=status.HTTP_201_CREATED)
async def create_a_blog(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    return {
        'message': 'created',
        'data': new_blog
    }

"""
This method is used to get all the blogs from the database

:param db: Session
:return object | exception
"""

@app.get('/blog', tags=['Blog'])
async def get_all_blogs(db: Session = Depends(get_db)):
    skip: int = 0
    limit: int = 100
    blogs = db.query(models.Blog).offset(skip).limit(limit).all()
    if blogs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No blogs found'
        )

    return {
        'message': 'success',
        'data': blogs
    }

"""
This method is used to get a particular blog from the database

:param blog_id: int
:param db: Session
:return object | exception
"""

@app.get('/blog/{blog_id}', tags=['Blog'])
async def get_a_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'The blog with id: {blog_id} not found'
        )

    return {
        'message': 'success',
        'data': blog
    }

"""
This method is used to update a blog in the database

:param blog_id: int
:param request: schemas.Blog
:return object | exception
"""

@app.put('/blog/{blog_id}', tags=['Blog'])
async def update_a_blog(blog_id: int, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)
    if blog.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'The blog with id: {blog_id} not found'
        )

    blog.update({'title': request.title, 'body': request.body}, synchronize_session=False)
    db.commit()

    return {
        'message': 'updated',
        'data': blog.first()
    }

"""
This method is used to delete a blog from the database

:param blog_id: int
:param db: Session
:return object | exception
"""

@app.delete('/blog/{blog_id}', tags=['Blog'])
async def delete_a_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)
    if blog.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'The blog with id: {blog_id} not found'
        )

    blog.delete(synchronize_session=False)
    db.commit()

    return {
        'message': 'deleted',
        'data': None
    }

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
