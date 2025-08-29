from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(32), unique=True, nullable=False)
    name = Column(String(128))
    phone = Column(String(32))
    is_subscribed = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    orders = relationship('Order', back_populates='user')

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    address = Column(String(256), nullable=False)
    categories = relationship('Category', back_populates='restaurant')
    products = relationship('Product', back_populates='restaurant')
    discounts = relationship('Discount', back_populates='restaurant')
    orders = relationship('Order', back_populates='restaurant')

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    products = relationship('Product', back_populates='category')
    restaurant = relationship('Restaurant', back_populates='categories')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.id'))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    price = Column(Float, nullable=False)
    discount_price = Column(Float)
    size = Column(String(32))
    photo = Column(String(256))
    is_available = Column(Boolean, default=True)
    stock = Column(Integer, default=0)
    category = relationship('Category', back_populates='products')
    order_items = relationship('OrderItem', back_populates='product')
    restaurant = relationship('Restaurant', back_populates='products')

class Discount(Base):
    __tablename__ = 'discounts'
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    description = Column(Text)
    date_start = Column(DateTime)
    date_end = Column(DateTime)
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    category = relationship('Category')
    product = relationship('Product')
    restaurant = relationship('Restaurant', back_populates='discounts')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    status = Column(String(32), default='new')  # new, paid, confirmed, cancelled
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    paid_at = Column(DateTime)
    admin_comment = Column(Text)
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order')
    receipt = relationship('Receipt', uselist=False, back_populates='order')
    restaurant = relationship('Restaurant', back_populates='orders')

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    discount_price = Column(Float)
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')

class Receipt(Base):
    __tablename__ = 'receipts'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    file_path = Column(String(256))
    uploaded_at = Column(DateTime, server_default=func.now())
    order = relationship('Order', back_populates='receipt')

class AdminUser(Base):
    __tablename__ = 'admin_users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(32), unique=True, nullable=False)
    name = Column(String(128))
    password_hash = Column(String(256))  # если потребуется для веб-панели 