from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.home, name='home'),
    path('text-to-image/', views.text_to_image, name='text_to_image'),
    path('sketch-to-image/', views.sketch_to_image, name='sketch_to_image'),
    path('product-ad-enhancer/', views.product_ad_enhancer, name='product_ad_enhancer'),
    path('image-editor/', views.image_editor, name='image_editor'),
    path('youtube-thumbnail/', views.youtube_thumbnail_generator, name='youtube_thumbnail_generator'),
    # API endpoints
    path('api/generate-text-to-image/', views.generate_text_to_image, name='generate_text_to_image_api'),
    path('api/enhance-product-ad/', views.generate_product_ad_enhancer, name='generate_product_ad_enhancer_api'),
    path('api/generate-sketch-to-image/', views.generate_sketch_to_image, name='generate_sketch_to_image_api'),
    path('api/edit-image/', views.api_edit_image, name='api_edit_image'),
    path('api/generate-youtube-thumbnail/', views.api_generate_youtube_thumbnail, name='api_generate_youtube_thumbnail'),
]
