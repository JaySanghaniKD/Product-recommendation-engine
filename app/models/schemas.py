from datetime import datetime
from typing import List, Optional, Union, Dict

from pydantic import BaseModel, Field


# Product-related models
class Dimensions(BaseModel):
    width: float
    height: float
    depth: float


class Review(BaseModel):
    rating: int
    comment: str
    date: datetime
    reviewerName: str
    reviewerEmail: str


class Meta(BaseModel):
    createdAt: datetime
    updatedAt: datetime
    barcode: str
    qrCode: str


class ProductBase(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    discountPercentage: Optional[float] = None
    rating: Optional[float] = None
    stock: Optional[int] = None
    tags: Optional[List[str]] = None
    sku: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dimensions] = None
    warrantyInformation: Optional[str] = None
    shippingInformation: Optional[str] = None
    availabilityStatus: Optional[str] = None
    returnPolicy: Optional[str] = None
    minimumOrderQuantity: Optional[int] = None
    images: Optional[List[str]] = None
    thumbnail: Optional[str] = None


class ProductInput(ProductBase):
    reviews: Optional[List[Review]] = None
    meta: Optional[Meta] = None


class ProductStored(ProductInput):
    _id: Optional[str] = None  # MongoDB ObjectId as string


class CategoryMaster(BaseModel):
    category_id: str
    name: str
    description: str
    parent_category_id: Optional[str] = None


# User interaction models
class UserInteractionBase(BaseModel):
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)


class SearchInteractionDetail(BaseModel):
    query: str
    llm_extracted_category_phrases: Optional[List[str]] = None
    matched_pinecone_categories: Optional[List[str]] = None
    llm_filter_criteria: Optional[Dict] = None
    retrieved_product_ids_from_db: Optional[List[int]] = None
    final_ranked_product_ids: Optional[List[int]] = None


class ViewProductInteractionDetail(BaseModel):
    product_id: int
    product_title: str


class AddToCartInteractionDetail(BaseModel):
    product_id: int
    product_title: str
    quantity: int


class UserInteractionStored(UserInteractionBase):
    interaction_type: str  # e.g., "search", "view_product", "add_to_cart"
    details: Union[
        SearchInteractionDetail,
        ViewProductInteractionDetail,
        AddToCartInteractionDetail,
    ]


# Cart models
class CartItemBase(BaseModel):
    product_id: int
    quantity: int


class CartItem(CartItemBase):
    title: str
    price: float
    thumbnail: Optional[str] = None


class UserCartStored(BaseModel):
    user_id: str
    items: List[CartItem] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


# LLM-related output models
class LLMQueryAnalysisOutput(BaseModel):
    descriptive_category_phrases: List[str]
    filter_criteria: Optional[Dict] = None
    extracted_tags: Optional[List[str]] = None
    user_intent_summary: str


class LLMProductRankDetail(BaseModel):
    product_id: int
    title: str
    justification: str
    rank: int
    price: float
    thumbnail: Optional[str] = None


class LLMFinalProductSelectionOutput(BaseModel):
    ranked_products: List[LLMProductRankDetail]
    overall_summary: Optional[str] = None


# API request/response models
class SearchApiRequest(BaseModel):
    user_id: str
    query: str


class SearchApiResponseProduct(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    thumbnail: Optional[str] = None
    justification: Optional[str] = None


class SearchApiResponse(BaseModel):
    query_received: str
    user_id: str
    search_results: List[SearchApiResponseProduct]
    message: Optional[str] = None


class CartActionRequest(BaseModel):
    user_id: str
    product_id: int
    quantity: Optional[int] = 1


class UserCartApiResponse(UserCartStored):
    pass
