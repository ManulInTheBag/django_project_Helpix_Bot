from django.conf import settings
from django.db import models
from django.utils import timezone


class Profile(models.Model):
	external_id = models.PositiveIntegerField(
		verbose_name='ID юзера',
		)
	name = models.TextField(
		verbose_name='Имя юзера',
		)

	def __str__(self):
		return f'#{self.external_id} {self.name}'

	class Meta:
		verbose_name = 'Профиль'
		verbose_name_plural = 'Профили'

class Message(models.Model):
	profile = models.ForeignKey(
		to='bot.Profile',
		verbose_name='Профиль',
		on_delete=models.PROTECT,
	)
	text = models.TextField(
		verbose_name='Текст',
	)
	created_at = models.DateTimeField(
		verbose_name='Время получения',
		auto_now_add=True,
	)

	def __str__(self):
		return f'Сообщение {self.pk} от {self.profile}'

	class Meta:
		verbose_name = 'Сообщение'
		verbose_name_plural = 'Сообщения'