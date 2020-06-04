from django.contrib.auth.models import User
from django.db import models

# Create your models here.

from FrontEnd.webapp.designer.settings import DEFAULT_PROFILE_IMG

PROFILE_ROLE = (
	('D', 'Default'),
	('S', 'SuperUser'),
	('A', 'Administrator'),
	('R', 'ReadOnly'),
)


class Base(models.Model):
	IsEnabled = models.BooleanField('Enabled', default=True)
	CreatedAt = models.DateTimeField('Created At', auto_now_add=True)
	LastModified = models.DateTimeField('Last Modified', auto_now=True)

	class Meta:
		abstract = True


# Everyone can create a profile on our system
class Profile(Base):
	IsUser = models.OneToOneField(User, on_delete=models.CASCADE)
	Lang = models.CharField('Language', max_length=2)

	ProfileInfo = models.TextField('Profile Info', blank=True)

	MailNotification = models.BooleanField('Mail notification', default=True)
	StayLoggedIn = models.BooleanField('Stay Logged In', default=False)

	# any restrictions on project
	Role = models.CharField('Role', max_length=1, choices=PROFILE_ROLE, default='D')

	LoginCount = models.IntegerField(default=0)

	def fullName(self):
		return self.IsUser.first_name + ' ' + self.IsUser.last_name

	def __str__(self):
		return self.IsUser.first_name + " " + self.IsUser.last_name


class taskProperty(Base):
	Name = models.TextField('Property name', blank=True)
	Form = models.TextField('Form name', blank=True)
	IsChecked = models.BooleanField('Is Checked', default=False)
	Owner = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)