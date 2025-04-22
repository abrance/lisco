from typing import Optional, List

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from pkg.db.db import get_db

from pkg.server.http.server import AppServer
from pkg.db.model.model import (
    User as UserModel,
    Image as ImageModel,
    InstanceAttr as InstanceAttrModel,
    Instance as InstanceModel,
    Quote as QuoteModel,
    QuoteFile as QuoteFileModel,
)
from pkg.util.log.log import logger

APP_NAME = "resource"


class ResourceAppServer(AppServer):
    def __init__(self):
        super().__init__("/" + APP_NAME)


resource_app_server = ResourceAppServer()
resource_app = resource_app_server.get_app()


@resource_app.get("/")
def read_root():
    return {"Hello": "World, " + APP_NAME}


class User(BaseModel):
    id: Optional[int] = None
    name: str
    phone: str
    password: str
    description: str


@resource_app.post("/users/", response_model=User)
def create_user(user: User, db: Session = Depends(get_db)):
    db_user = UserModel(**user.dict())  # 将Pydantic模型转换为数据库模型
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user


@resource_app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return User(
        id=db_user.id,
        name=db_user.name,
        phone=db_user.phone,
        password=db_user.password,
        description=db_user.description,
    )


@resource_app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = updated_user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return User(
        id=db_user.id,
        name=db_user.name,
        phone=db_user.phone,
        password=db_user.password,
        description=db_user.description,
    )


@resource_app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}


@resource_app.get("/users/")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    logger.info("users: {}".format(users))
    return users


class ImageSchema(BaseModel):
    id: Optional[int] = None
    name: str
    title_type: str
    title: str
    create_user_id: int
    path: str
    description: Optional[str] = None

    class Config:
        orm_mode = True  # 这将允许 Pydantic 模型从 ORM 模型实例中读取数据


@resource_app.post("/images/", response_model=ImageSchema)
def create_image(image: ImageSchema, db: Session = Depends(get_db)):
    db_image = ImageModel(**image.dict())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return ImageSchema.from_orm(db_image)


@resource_app.get("/images/{image_id}", response_model=ImageSchema)
def read_image(image_id: int, db: Session = Depends(get_db)):
    db_image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return ImageSchema.from_orm(db_image)


@resource_app.put("/images/{image_id}", response_model=ImageSchema)
def update_image(
    image_id: int, updated_image: ImageSchema, db: Session = Depends(get_db)
):
    db_image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    image_data = updated_image.dict(exclude_unset=True)
    for key, value in image_data.items():
        setattr(db_image, key, value)

    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return ImageSchema.from_orm(db_image)


@resource_app.delete("/images/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    db_image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    db.delete(db_image)
    db.commit()
    return {"detail": "Image deleted"}


@resource_app.get("/images/", response_model=List[ImageSchema])
def read_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    images = db.query(ImageModel).offset(skip).limit(limit).all()
    return [ImageSchema.from_orm(image) for image in images]


class InstanceSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class InstanceAttrSchema(BaseModel):
    id: Optional[int] = None
    name: str
    attr_id: int
    attr_value: str
    instance_id: int

    class Config:
        orm_mode = True


@resource_app.post("/instance_attrs/", response_model=InstanceAttrSchema)
def create_instance_attr(attr: InstanceAttrSchema, db: Session = Depends(get_db)):
    db_attr = InstanceAttrModel(**attr.dict())
    db.add(db_attr)
    db.commit()
    db.refresh(db_attr)
    return InstanceAttrSchema.from_orm(db_attr)


@resource_app.get("/instance_attrs/{attr_id}", response_model=InstanceAttrSchema)
def read_instance_attr(attr_id: int, db: Session = Depends(get_db)):
    db_attr = (
        db.query(InstanceAttrModel).filter(InstanceAttrModel.id == attr_id).first()
    )
    if db_attr is None:
        raise HTTPException(status_code=404, detail="Instance attribute not found")
    return InstanceAttrSchema.from_orm(db_attr)


@resource_app.put("/instance_attrs/{attr_id}", response_model=InstanceAttrSchema)
def update_instance_attr(
    attr_id: int, updated_attr: InstanceAttrSchema, db: Session = Depends(get_db)
):
    db_attr = (
        db.query(InstanceAttrModel).filter(InstanceAttrModel.id == attr_id).first()
    )
    if db_attr is None:
        raise HTTPException(status_code=404, detail="Instance attribute not found")

    attr_data = updated_attr.dict(exclude_unset=True)
    for key, value in attr_data.items():
        setattr(db_attr, key, value)

    db.add(db_attr)
    db.commit()
    db.refresh(db_attr)
    return InstanceAttrSchema.from_orm(db_attr)


@resource_app.delete("/instance_attrs/{attr_id}")
def delete_instance_attr(attr_id: int, db: Session = Depends(get_db)):
    db_attr = (
        db.query(InstanceAttrModel).filter(InstanceAttrModel.id == attr_id).first()
    )
    if db_attr is None:
        raise HTTPException(status_code=404, detail="Instance attribute not found")

    db.delete(db_attr)
    db.commit()
    return {"detail": "Instance attribute deleted"}


@resource_app.get("/instance_attrs/", response_model=List[InstanceAttrSchema])
def read_instance_attrs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    attrs = db.query(InstanceAttrModel).offset(skip).limit(limit).all()
    return [InstanceAttrSchema.from_orm(attr) for attr in attrs]


@resource_app.post("/instances/", response_model=InstanceSchema)
def create_instance(instance: InstanceSchema, db: Session = Depends(get_db)):
    db_instance = InstanceModel(**instance.dict())
    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)
    return InstanceSchema.from_orm(db_instance)


@resource_app.get("/instances/{instance_id}", response_model=InstanceSchema)
def read_instance(instance_id: int, db: Session = Depends(get_db)):
    db_instance = (
        db.query(InstanceModel).filter(InstanceModel.id == instance_id).first()
    )
    if db_instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return InstanceSchema.from_orm(db_instance)


@resource_app.put("/instances/{instance_id}", response_model=InstanceSchema)
def update_instance(
    instance_id: int, updated_instance: InstanceSchema, db: Session = Depends(get_db)
):
    db_instance = (
        db.query(InstanceModel).filter(InstanceModel.id == instance_id).first()
    )
    if db_instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")

    instance_data = updated_instance.dict(exclude_unset=True)
    for key, value in instance_data.items():
        setattr(db_instance, key, value)

    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)
    return InstanceSchema.from_orm(db_instance)


@resource_app.delete("/instances/{instance_id}")
def delete_instance(instance_id: int, db: Session = Depends(get_db)):
    db_instance = (
        db.query(InstanceModel).filter(InstanceModel.id == instance_id).first()
    )
    if db_instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")

    db.delete(db_instance)
    db.commit()
    return {"detail": "Instance deleted"}


@resource_app.get("/instances/", response_model=List[InstanceSchema])
def read_instances(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    instances = db.query(InstanceModel).offset(skip).limit(limit).all()
    return [InstanceSchema.from_orm(instance) for instance in instances]


class QuoteSchema(BaseModel):
    id: Optional[int] = None
    name: str
    location: Optional[str] = None
    content: Optional[str] = None
    create_user_id: int

    class Config:
        orm_mode = True


class QuoteFileSchema(BaseModel):
    id: Optional[int] = None
    name: str
    quote_type: str
    suffix: str
    quote_id: int
    path: Optional[str] = None
    urls: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


@resource_app.post("/quotes/", response_model=QuoteSchema)
def create_quote(quote: QuoteSchema, db: Session = Depends(get_db)):
    db_quote = QuoteModel(**quote.dict())
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    return QuoteSchema.from_orm(db_quote)


@resource_app.get("/quotes/{quote_id}", response_model=QuoteSchema)
def read_quote(quote_id: int, db: Session = Depends(get_db)):
    db_quote = db.query(QuoteModel).filter(QuoteModel.id == quote_id).first()
    if db_quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return QuoteSchema.from_orm(db_quote)


@resource_app.put("/quotes/{quote_id}", response_model=QuoteSchema)
def update_quote(
    quote_id: int, updated_quote: QuoteSchema, db: Session = Depends(get_db)
):
    db_quote = db.query(QuoteModel).filter(QuoteModel.id == quote_id).first()
    if db_quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")

    quote_data = updated_quote.dict(exclude_unset=True)
    for key, value in quote_data.items():
        setattr(db_quote, key, value)

    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    return QuoteSchema.from_orm(db_quote)


@resource_app.delete("/quotes/{quote_id}")
def delete_quote(quote_id: int, db: Session = Depends(get_db)):
    db_quote = db.query(QuoteModel).filter(QuoteModel.id == quote_id).first()
    if db_quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")

    db.delete(db_quote)
    db.commit()
    return {"detail": "Quote deleted"}


@resource_app.get("/quotes/", response_model=List[QuoteSchema])
def read_quotes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    quotes = db.query(QuoteModel).offset(skip).limit(limit).all()
    return [QuoteSchema.from_orm(quote) for quote in quotes]


@resource_app.post("/quote_files/", response_model=QuoteFileSchema)
def create_quote_file(file: QuoteFileSchema, db: Session = Depends(get_db)):
    db_file = QuoteFileModel(**file.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return QuoteFileSchema.from_orm(db_file)


@resource_app.get("/quote_files/{file_id}", response_model=QuoteFileSchema)
def read_quote_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(QuoteFileModel).filter(QuoteFileModel.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=404, detail="Quote file not found")
    return QuoteFileSchema.from_orm(db_file)


@resource_app.put("/quote_files/{file_id}", response_model=QuoteFileSchema)
def update_quote_file(
    file_id: int, updated_file: QuoteFileSchema, db: Session = Depends(get_db)
):
    db_file = db.query(QuoteFileModel).filter(QuoteFileModel.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=404, detail="Quote file not found")

    file_data = updated_file.dict(exclude_unset=True)
    for key, value in file_data.items():
        setattr(db_file, key, value)

    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return QuoteFileSchema.from_orm(db_file)


@resource_app.delete("/quote_files/{file_id}")
def delete_quote_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(QuoteFileModel).filter(QuoteFileModel.id == file_id).first()
    if db_file is None:
        raise HTTPException(status_code=404, detail="Quote file not found")

    db.delete(db_file)
    db.commit()
    return {"detail": "Quote file deleted"}


@resource_app.get("/quote_files/", response_model=List[QuoteFileSchema])
def read_quote_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    files = db.query(QuoteFileModel).offset(skip).limit(limit).all()
    return [QuoteFileSchema.from_orm(file) for file in files]
