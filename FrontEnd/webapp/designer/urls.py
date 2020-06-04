from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView

from FrontEnd.webapp.designer import views, userViews
from FrontEnd.webapp.webapp import settings

urlpatterns = [
	path('', views.home),
	path('form1', views.form1),
	path('form11', views.form11),
	path('form12', views.form12),
	path('form13', views.form13),
	path('form14', views.form14),
	path('form2', views.form2),
	path('form21', views.form21),
	path('form22', views.form22),
	path('form31', views.form31),
	path('form32', views.form32),
	path('form41', views.form41),
	path('form42', views.form42),
	path('form43', views.form43),
# user
	path('login/', userViews.userLogin),
	path('reset/', userViews.reset),
	path('logout/', userViews.userLogout),
	path('accounts/login/', userViews.userLogin),
	path('register/', userViews.register),
	path('profile/', userViews.getProfile),
	path('dpwconfirm/<uid>/<token>/', userViews.confirmNewPassword),

	path('imprint/', TemplateView.as_view(template_name='designer/templates/imprint.html')),
	path('privacy/', TemplateView.as_view(template_name='designer/templates/privacy.html')),
	#ajax urls
	#path('phrases', views.getjobads)
]

