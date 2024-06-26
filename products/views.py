from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from django.http import Http404
from .serializer import CategorySerializer, ProductCommentSerializer, ProductSerializer, ProductImageSerializer
from .models import Category, Product, ProductImage, ProductComment
from .helpers import custom_response, parse_request
from rest_framework.parsers import JSONParser
from json import JSONDecodeError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .pagination import ProductCreatePagination
from rest_framework.pagination import PageNumberPagination

User = get_user_model()

class CategoryAPIView(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return custom_response('Get all categories successfully!', 'Success', serializer.data, 200)
        except Exception as e:
            return custom_response('Get all categoriese failed !', 'Error', None, 400)
            
    def post(self, request):
        data = parse_request(request)
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return custom_response('Create category successfully!', 'Success', serializer.data, 201)
        else:
            return custom_response('Create category failed !', 'Error', serializer.errors, 400)
        
class CategoryDetailAPIView(views.APIView):
    permission_classes = [AllowAny]
    
    def get_object(self, id_slug):
        try:    
            return Category.objects.get(id = id_slug)
        except:
            return Http404("Category not found")
        
    def get(self, id_slug, format = None):
        try:
            category = self.get_object(id_slug)
            serializer = CategorySerializer(category)
            return custom_response('Get category successfully !', 'Success', serializer.data, 200)
        except:
            return custom_response('Get category failed !', 'Error', 'Category not found !', 400)
        
    def put(self, request, id_slug):
        try:
            data = parse_request(request)
            category = self.get_object(id_slug)
            serializer = CategorySerializer(category, data=data)
            if serializer.is_valid():
                serializer.save()
                return custom_response('Update category successfully !', 'Success', serializer.data, 200)
            else:
                return custom_response('Update category failed !', 'Error', serializer.errors, 400)
        except:
                return custom_response('Update category failed !', 'Error', 'Category not found!', 400)
            
    def delete(self, request,id_slug):
        try:
            category= self.get_object(id_slug)
            category.delete()
            return custom_response('Delete category successfully!', 'Success', {"category_id" : id_slug}, 204)
        except:
            return custom_response('Delete category failed!', 'Error', 'Category not found!', 400)
        
class ProductViewAPI(views.APIView ):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            page = request.query_params.get('page', 1)
            limit = request.query_params.get('limit', 10)
            keyword = request.query_params.get('keyword', '')
            category = request.query_params.get('category', '')
            min_price = request.query_params.get('min_price', 0)
            max_price = request.query_params.get('max_price', float('inf'))
            
            products = Product.objects.all()

            if keyword:
                products = products.filter(name__icontains=keyword)

            if category:
                try:
                    category_obj = Category.objects.get(name__icontains=category)
                    products = products.filter(category_id=category_obj)
                except Category.DoesNotExist:
                    products = products.none()

            if min_price:
                products = products.filter(price__gte=min_price)

            if max_price and max_price != float('inf'):
                products = products.filter(price__lte=max_price)
            
            total_records = products.count()
            paginator = PageNumberPagination()
            paginator.page_size = int(limit)
            paginated_products = paginator.paginate_queryset(products, request)

            total_pages = paginator.page.paginator.num_pages

            serializer = ProductSerializer(paginated_products, many=True)
            
            context = {'data': serializer.data, 'page': int(page), 'limit': int(limit),  'total_page': total_pages,'total_record': total_records}
            return custom_response('Get all products successfully!', 'Success', context, 200)
        except:
            return custom_response('Get all products failed!', 'Error', None, 400)
        
    def post(self, request):
        try:
            data = parse_request(request)
            category = Category.objects.get(id=data['category_id'])
            product = Product(
                name = data['name'],
                unit=data['unit'],
                price=data['price'],
                discount=data['discount'],
                amount=data['amount'],
                thumbnail=data['thumbnail'],
 # gán category đã tìm được vào field category_id
                category_id=category
            )
            product.save()
            serializer = ProductSerializer(product)
            return custom_response('Create product successfully!','Success', serializer.data, 201)
        except Exception as e:
            return custom_response('Create product failed!', 'Error', {'Error' : str(e)}, 400)    
        
class ProductDetailAPIView(views.APIView):
    permission_classes = [AllowAny]
    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except:
            raise Http404
        
    def get(self, request, id, format=None):
        try:
            product = self.get_object(id)
            serializer = ProductSerializer(product)
            return custom_response('Get product successfully!', 'Success', serializer.data, 200)
        except:
            return custom_response('Get product failed!', 'Error', "Product not found!", 400)
        
    def put(self, request, id):
        try:
            data = parse_request(request)
            product = self.get_object(id)
            serializer = ProductSerializer(product, data=data)
            if serializer.is_valid():
                serializer.save()
                return custom_response('Update product successfully!', 'Success', serializer.data, 200)
            else:
                return custom_response('Update product failed', 'Error', serializer.errors, 400)
        except:
            return custom_response('Update product failed', 'Error', "Category not found!", 400)
    def delete(self, request, id):
        try:
            product = self.get_object(id)
            product.delete()
            return custom_response('Delete product successfully!', 'Success', {"product_id": id}, 204)
        except:
            return custom_response('Delete product failed!', 'Error', "Product not found!", 400)
        
        
class ProductImageAPIView(views.APIView):
    def get(self, request, product_id_slug):
        try:
            product_images = ProductImage.objects.filter(product_id=product_id_slug).all()
            serializers = ProductImageSerializer(product_images, many=True)
            return custom_response('Get all product images successfully!', 'Success', serializers.data, 200)
        except:
            return custom_response('Get all product images failed!', 'Error', 'Product images not found', 
            400)
    def post(self, request, product_id_slug):
        try:
            data = parse_request(request)
            product = Product.objects.get(id=data['product_id'])
            product_image = ProductImage(
            product_id=product,
            image_url=data['image_url']
            )
            product_image.save()
            serializer = ProductImageSerializer(product_image)
            return custom_response('Create product image successfully!', 'Success', serializer.data, 201)
        except Exception as e:
            return custom_response('Create product image failed', 'Error', {"error": str(e)}, 400)
        
        
class ProductImageDetailAPIView(views.APIView):
    def get_object(self, id_slug):
        try:
            return ProductImage.objects.get(id=id_slug)
        except:
            raise Http404
    def get_object_with_product_id(self, product_id_slug, id_slug):
        try:
            return ProductImage.objects.get(product_id=product_id_slug, id=id_slug)
        except:
            raise Http404
    def get(self, request, product_id_slug, id_slug, format=None):
        try:
            product_image = self.get_object(id_slug)
            serializer = ProductImageSerializer(product_image)
            return custom_response('Get product image successfully!', 'Success', serializer.data, 200)
        except:
            return custom_response('Get product image failed!', 'Error', "Product image not found!", 400)
    def put(self, request, product_id_slug, id_slug):
        try:
            data = parse_request(request)
            product_image = self.get_object_with_product_id(product_id_slug, id_slug)
            serializer = ProductImageSerializer(product_image, data=data)
            if serializer.is_valid():
                serializer.save()
                return custom_response('Update product image successfully!', 'Success', serializer.data, 200)
            else:
                return custom_response('Update product image failed', 'Error', serializer.errors, 400)
        except:
            return custom_response('Update product image failed', 'Error', "Product image not found!", 400)
    def delete(self, request, product_id_slug, id_slug):
        try:
            product_image = self.get_object_with_product_id(product_id_slug, id_slug)
            product_image.delete()
            return custom_response('Delete product image successfully!', 'Success', {"product_image_id": 
            id_slug}, 204)
        except:
            return custom_response('Delete product image failed!', 'Error', "Product image not found!", 
            400)
            
class ProductCommentAPIView(views.APIView):
    permission_classes = [AllowAny]
    def get(self, request, product_id_slug):
        try:
            product_comments = ProductComment.objects.filter(product_id=product_id_slug).all()
            serializers = ProductCommentSerializer(product_comments, many=True)
            return custom_response('Get all product comments successfully!', 'Success', serializers.data, 
            200)
        except:
            return custom_response('Get all product comments failed!', 'Error', None, 400)
        
    def post(self, request, product_id_slug):
        try:
            data = parse_request(request)
            product = Product.objects.get(id=data['product_id'])
            user = User.objects.get(id=data['user_id'])
            product_comment = ProductComment(
            product_id=product,
            rating=data['rating'],
            comment=data['comment'],
            user_id=user,
            parent_id=data['parent_id']
            )
            product_comment.save()
            serializer = ProductCommentSerializer(product_comment)
            return custom_response('Create product comment successfully!', 'Success', serializer.data, 201)
        except Exception as e:
            return custom_response('Create product comment failed', 'Error', {"error": str(e)}, 400)

class ProductCommentDetailAPIView(views.APIView):
    def get_object(self, id_slug):
        try:
            return ProductComment.objects.get(id=id_slug)
        except:
            raise Http404
    def get_object_with_product_id(self, product_id_slug, id_slug):
        try:
            return ProductComment.objects.get(product_id=product_id_slug, id=id_slug)
        except:
            raise Http404
    def get(self, request, product_id_slug, id_slug, format=None):
        try:
            product_comment = self.get_object(id_slug)
            serializer = ProductCommentSerializer(product_comment)
            return custom_response('Get product comment successfully!', 'Success', serializer.data, 200)
        except:
            return custom_response('Get product comment failed!', 'Error', "Product comment not found!", 
                400)
    def put(self, request, product_id_slug, id_slug):
        try:
            data = parse_request(request)
            product_comment = self.get_object_with_product_id(product_id_slug, id_slug)
            serializer = ProductCommentSerializer(product_comment, data=data)
            if serializer.is_valid():
                serializer.save()
                return custom_response('Update product comment successfully!', 'Success', serializer.data, 
                200)
            else:
                return custom_response('Update product comment failed', 'Error', serializer.errors, 400)
        except:
            return custom_response('Update product comment failed', 'Error', "Product comment not found!", 400)
    def delete(self, request, product_id_slug, id_slug):
        try:
            product_comment = self.get_object_with_product_id(product_id_slug, id_slug)
            product_comment.delete()
            return custom_response('Delete product comment successfully!', 'Success', 
            {"product_comment_id": id_slug},
            204)
        except:
            return custom_response('Delete product comment failed!', 'Error', "Product comment not found!", 400)