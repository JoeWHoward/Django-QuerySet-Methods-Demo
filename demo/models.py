from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import (
    Count,
    Exists,
    OuterRef,
    Window,
    F,
    Subquery,
    ExpressionWrapper,
    Avg, Case, When, Value, Sum, Func,
)
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Rank, Length, StrIndex, Substr, JSONObject


class PersonQuerySet(models.QuerySet):
    def with_num_books(self):
        return self.annotate(num_books=Count("books"))

    def has_rating_on_any_book(self):
        return self.filter(
            Exists(Book.objects.filter(author=OuterRef("id"), ratings__isnull=False))
        )

    def with_total_book_rating_avg(self):
        return self.annotate(
            avg_rating=Avg("books__ratings__value")
        )

    def with_experience_annotated(self):
        return self.annotate(
            total_books_length=Sum('books__length')
        ).annotate(
            experience_level=Case(
                When(
                    total_books_length__gte=10000, then=Value("A master")
                ),
                When(
                    total_books_length__gte=1000, then=Value("Very experienced"),
                ),
                When(
                    total_books_length__gte=500, then=Value("Experienced"),
                ),
                When(
                    total_books_length__gte=100, then=Value("Beginner")
                ),
                default=Value("Novice"),
                output_field=models.CharField()
            )
        )

    def with_last_book_title(self):
        return self.annotate(
            latest_book_title=Subquery(
                Book.objects.filter(author=OuterRef("id")).order_by('-pk').values("title__text")[:1]
            )
        )

    def with_first_last_name(self):
        return self.annotate(
            str_index=StrIndex('name', Value(' '))
        ).annotate(
            first_name=Substr('name', 1, F('str_index') - 1),
            last_name=Substr('name', F('str_index') + 1, Length('name'))
        )

    def with_first_last_name_json(self):
        return self.with_first_last_name().annotate(
            json=JSONObject(
                first_name='first_name',
                last_name='last_name',
                occupation='occupation'
            )
        )

    def with_first_last_name_json_alternate(self):
        return self.with_first_last_name().annotate(
            json=Func(
                Value('first_name'), 'first_name',
                Value('last_name'), 'last_name',
                Value('occupation'), 'occupation',
                function='JSONB_BUILD_OBJECT'
            )
        )




# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=12)
    occupation = models.CharField(max_length=20)
    address = models.ForeignKey(
        "Address", related_name="occupant", on_delete=models.PROTECT
    )

    objects = PersonQuerySet.as_manager()


class Address(models.Model):
    street = models.CharField(max_length=50)
    street_number = models.IntegerField()
    zip_code = models.IntegerField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)


class Book(models.Model):
    author = models.ForeignKey("Person", related_name="books", on_delete=models.CASCADE)
    title = models.OneToOneField("Title", on_delete=models.CASCADE)
    length = models.IntegerField(validators=[MinValueValidator(0)])


class Title(models.Model):
    text = models.CharField(max_length=50)


class Tag(models.Model):
    related_books = models.ManyToManyField(
        "Book",
        related_name="tags",
    )


class Rating(models.Model):
    target = models.ForeignKey("Book", related_name="ratings", on_delete=models.CASCADE)
    value = models.IntegerField()
