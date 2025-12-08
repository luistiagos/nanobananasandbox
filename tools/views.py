from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import uuid
from SimplerLLM import ImageGenerator, ImageProvider, ImageSize


def home(request):
    """Home page with cards for all three AI image tools."""
    return render(request, 'home.html')


def text_to_image(request):
    """Text to Image tool page."""
    return render(request, 'text_to_image.html')


def sketch_to_image(request):
    """Sketch to Image tool page."""
    return render(request, 'sketch_to_image.html')


def product_ad_enhancer(request):
    """Product Ad Enhancer tool page."""
    return render(request, 'product_ad_enhancer.html')


@csrf_exempt
def generate_text_to_image(request):
    """API endpoint to generate image from text using SimplerLLM."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Get parameters from request
        import json
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
        size = data.get('size', 'square').lower()

        # Validate prompt
        if not prompt:
            return JsonResponse({'error': 'Prompt is required'}, status=400)

        # Map size string to ImageSize enum
        size_map = {
            'square': ImageSize.SQUARE,
            'horizontal': ImageSize.HORIZONTAL,
            'vertical': ImageSize.VERTICAL
        }
        image_size = size_map.get(size, ImageSize.SQUARE)

        # Create image generator instance
        img_gen = ImageGenerator.create(provider=ImageProvider.GOOGLE_GEMINI)

        # Generate unique filename
        filename = f"text_to_image_{uuid.uuid4().hex}.png"
        output_path = os.path.join(settings.MEDIA_ROOT, 'generated_images', filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Generate image
        img_gen.generate_image(
            prompt=prompt,
            size=image_size,
            output_format="file",
            output_path=output_path
        )

        # Return image URL
        image_url = f"{settings.MEDIA_URL}generated_images/{filename}"
        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'filename': filename
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


@csrf_exempt
def generate_product_ad_enhancer(request):
    """API endpoint to enhance product photos using SimplerLLM."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Check if file was uploaded
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file uploaded'}, status=400)

        uploaded_file = request.FILES['image']

        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return JsonResponse({
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }, status=400)

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if uploaded_file.size > max_size:
            return JsonResponse({
                'error': 'File size too large. Maximum size is 10MB.'
            }, status=400)

        # Create upload directory
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Save uploaded file temporarily
        temp_filename = f"upload_{uuid.uuid4().hex}{file_ext}"
        temp_path = os.path.join(upload_dir, temp_filename)

        with open(temp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Create image generator instance
        img_gen = ImageGenerator.create(provider=ImageProvider.GOOGLE_GEMINI)

        # Generate output filename
        output_filename = f"product_enhancer_{uuid.uuid4().hex}.png"
        output_path = os.path.join(settings.MEDIA_ROOT, 'generated_images', output_filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Professional studio enhancement prompt
        enhancement_prompt = """Transform this product photo into a professional studio shot with high-end commercial photography quality.

Apply these enhancements:
- Professional three-point studio lighting (key light, fill light, rim light)
- Clean, minimalist background (pure white or subtle gradient)
- Sharp focus on the product with perfect clarity
- Remove any distractions, clutter, or background objects
- Enhance product details, colors, and textures
- Add natural shadows and reflections for depth
- Create a high-end, luxury feel
- Make it look like a professional advertisement or e-commerce product photo

Maintain the product's exact appearance while elevating the overall presentation to studio quality."""

        # Enhance the product image
        img_gen.edit_image(
            image_source=temp_path,
            edit_prompt=enhancement_prompt,
            size=ImageSize.HORIZONTAL,
            output_format="file",
            output_path=output_path,
            model="gemini-3-pro-image-preview"
        )

        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass

        # Return enhanced image URL
        image_url = f"{settings.MEDIA_URL}generated_images/{output_filename}"
        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'filename': output_filename
        })

    except Exception as e:
        # Clean up temp file if it exists
        try:
            if 'temp_path' in locals():
                os.remove(temp_path)
        except:
            pass

        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


@csrf_exempt
def generate_sketch_to_image(request):
    """API endpoint to transform sketches into realistic images using SimplerLLM."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Check if file was uploaded
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No sketch image uploaded'}, status=400)

        uploaded_file = request.FILES['image']

        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return JsonResponse({
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }, status=400)

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if uploaded_file.size > max_size:
            return JsonResponse({
                'error': 'File size too large. Maximum size is 10MB.'
            }, status=400)

        # Create upload directory
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Save uploaded sketch temporarily
        temp_filename = f"sketch_{uuid.uuid4().hex}{file_ext}"
        temp_path = os.path.join(upload_dir, temp_filename)

        with open(temp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Create image generator instance
        img_gen = ImageGenerator.create(provider=ImageProvider.GOOGLE_GEMINI)

        # Generate output filename
        output_filename = f"sketch_to_image_{uuid.uuid4().hex}.png"
        output_path = os.path.join(settings.MEDIA_ROOT, 'generated_images', output_filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Sketch to realistic transformation prompt
        transformation_prompt = """Transform this hand-drawn sketch into a photorealistic, high-quality photograph.
Maintain the exact composition, subject matter, and layout from the sketch, but enhance it with:
- Realistic details and textures
- Professional lighting and shadows
- Natural, vibrant colors
- High-definition quality
- Photographic depth and clarity
Make it look like a professional photograph while staying true to the original sketch's intent."""

        # Generate realistic image from sketch
        img_gen.generate_image(
            prompt=transformation_prompt,
            reference_images=[temp_path],
            size=ImageSize.HORIZONTAL,
            output_format="file",
            output_path=output_path,
            model="gemini-3-pro-image-preview"
        )

        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass

        # Return generated image URL
        image_url = f"{settings.MEDIA_URL}generated_images/{output_filename}"
        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'filename': output_filename
        })

    except Exception as e:
        # Clean up temp file if it exists
        try:
            if 'temp_path' in locals():
                os.remove(temp_path)
        except:
            pass

        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


def image_editor(request):
    """Image Editor tool page."""
    return render(request, 'image_editor.html')


@csrf_exempt
def api_edit_image(request):
    """API endpoint to edit images using AI with free-form text prompts."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Get the edit prompt
        edit_prompt = request.POST.get('prompt', '').strip()

        if not edit_prompt:
            return JsonResponse({'error': 'Edit prompt is required'}, status=400)

        # Determine the source image - either a new upload or a previously edited image
        source_image_path = None
        temp_path = None

        # Check if this is a new upload
        if 'image' in request.FILES:
            uploaded_file = request.FILES['image']

            # Validate file type
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext not in allowed_extensions:
                return JsonResponse({
                    'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                }, status=400)

            # Validate file size (max 10MB)
            max_size = 10 * 1024 * 1024  # 10MB in bytes
            if uploaded_file.size > max_size:
                return JsonResponse({
                    'error': 'File size too large. Maximum size is 10MB.'
                }, status=400)

            # Create upload directory
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            # Save uploaded file temporarily
            temp_filename = f"edit_upload_{uuid.uuid4().hex}{file_ext}"
            temp_path = os.path.join(upload_dir, temp_filename)

            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            source_image_path = temp_path

        # Check if this is editing a previously generated image
        elif 'current_image' in request.POST:
            current_image_filename = request.POST.get('current_image', '').strip()

            if current_image_filename:
                # Construct the full path to the previously generated image
                source_image_path = os.path.join(
                    settings.MEDIA_ROOT,
                    'generated_images',
                    current_image_filename
                )

                # Verify the file exists
                if not os.path.exists(source_image_path):
                    return JsonResponse({
                        'error': 'Referenced image not found. Please upload a new image.'
                    }, status=400)

        # If no source image was provided
        if not source_image_path:
            return JsonResponse({
                'error': 'No image provided. Please upload an image or reference an existing one.'
            }, status=400)

        # Create image generator instance
        img_gen = ImageGenerator.create(provider=ImageProvider.GOOGLE_GEMINI)

        # Generate output filename
        output_filename = f"edited_image_{uuid.uuid4().hex}.png"
        output_path = os.path.join(settings.MEDIA_ROOT, 'generated_images', output_filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Edit the image with the user's prompt
        img_gen.edit_image(
            image_source=source_image_path,
            edit_prompt=edit_prompt,
            size=ImageSize.HORIZONTAL,
            output_format="file",
            output_path=output_path,
            model="gemini-3-pro-image-preview"
        )

        # Clean up temporary file if it was uploaded
        if temp_path:
            try:
                os.remove(temp_path)
            except:
                pass

        # Return edited image URL
        image_url = f"{settings.MEDIA_URL}generated_images/{output_filename}"
        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'filename': output_filename
        })

    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and temp_path:
            try:
                os.remove(temp_path)
            except:
                pass

        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


def youtube_thumbnail_generator(request):
    """YouTube Thumbnail Generator tool page."""
    return render(request, 'youtube_thumbnail.html')


@csrf_exempt
def api_generate_youtube_thumbnail(request):
    """API endpoint to generate YouTube thumbnails with reference images."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Check if file was uploaded
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No reference image uploaded'}, status=400)

        # Get user's custom prompt
        user_prompt = request.POST.get('prompt', '').strip()
        if not user_prompt:
            return JsonResponse({'error': 'Thumbnail description is required'}, status=400)

        uploaded_file = request.FILES['image']

        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return JsonResponse({
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }, status=400)

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if uploaded_file.size > max_size:
            return JsonResponse({
                'error': 'File size too large. Maximum size is 10MB.'
            }, status=400)

        # Create upload directory
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Save uploaded file temporarily
        temp_filename = f"thumbnail_ref_{uuid.uuid4().hex}{file_ext}"
        temp_path = os.path.join(upload_dir, temp_filename)

        with open(temp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Create image generator instance
        img_gen = ImageGenerator.create(provider=ImageProvider.GOOGLE_GEMINI)

        # Generate output filename
        output_filename = f"youtube_thumbnail_{uuid.uuid4().hex}.png"
        output_path = os.path.join(settings.MEDIA_ROOT, 'generated_images', output_filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create optimized YouTube thumbnail prompt combining user input with best practices
        optimized_prompt = f"""Create a professional, high-CTR YouTube thumbnail featuring the person from the reference image.

User's Vision: {user_prompt}

Technical Requirements:
- Subject: The person from the reference image with an engaging, expressive face
- Composition: Strategic positioning with space for potential text overlay
- Lighting: Dramatic professional lighting with high contrast and rim lights
- Colors: Vibrant, bold colors that pop on screen using complementary color schemes
- Background: Dynamic and visually interesting, not cluttered, with depth
- Quality: High-definition, sharp focus, professional photography quality
- Style: Eye-catching, attention-grabbing, optimized for mobile viewing
- Expression: Genuine emotion that matches the video concept

YouTube Optimization:
- Must grab attention instantly in a crowded feed
- Clear and readable even at small thumbnail sizes (mobile optimization)
- Single strong focal point (the person's face and expression)
- High contrast for maximum visibility
- Professional and trustworthy appearance
- Designed to maximize click-through rate

Create a thumbnail that combines the user's vision with professional YouTube thumbnail best practices."""

        # Generate YouTube thumbnail with reference image
        img_gen.generate_image(
            prompt=optimized_prompt,
            reference_images=[temp_path],
            size=ImageSize.HORIZONTAL,  # 16:9 aspect ratio for YouTube (1280x720)
            output_format="file",
            output_path=output_path,
            model="gemini-3-pro-image-preview"
        )

        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass

        # Return generated thumbnail URL
        image_url = f"{settings.MEDIA_URL}generated_images/{output_filename}"
        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'filename': output_filename
        })

    except Exception as e:
        # Clean up temp file if it exists
        try:
            if 'temp_path' in locals():
                os.remove(temp_path)
        except:
            pass

        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)
