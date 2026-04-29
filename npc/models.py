from django.db import models

from item.models import Item
from tbac import mixins

# Create your models here.


class Friend(mixins.SearchableMixin):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=1000)
    in_room_description = models.CharField(max_length=1000)
    game = models.ForeignKey(
        "game.Game", related_name="friends", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "room.Room", related_name="friends", on_delete=models.CASCADE
    )

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="friends",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    objects = mixins.SessionManager()

    def __str__(self):
        return self.name


class Enemy(mixins.SearchableMixin):
    description = models.CharField(max_length=1000)
    game = models.ForeignKey(
        "game.Game", related_name="enemies", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "room.Room", related_name="enemies", on_delete=models.CASCADE
    )
    in_room_description = models.CharField(max_length=1000)
    health = models.IntegerField(default=100)
    damage = models.OneToOneField("game.DamageOutput", on_delete=models.CASCADE)
    auto_fight = models.BooleanField(default=True)

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="enemies",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    current_health = models.IntegerField(default=0)
    is_dead = models.BooleanField(default=False)

    objects = mixins.SessionManager()

    def get_dropped_items(self):
        if self.session is None:
            return self.game.items.base().filter(enemy_drop__enemy=self)
        return self.session.items.filter(enemy_drop__enemy=self)

    def __str__(self):
        return self.name


class EnemyDrop(models.Model):
    game = models.ForeignKey(
        "game.Game", related_name="enemy_drops", on_delete=models.CASCADE
    )
    enemy = models.ForeignKey("Enemy", related_name="drops", on_delete=models.CASCADE)
    item = models.OneToOneField(
        "item.Item", related_name="enemy_drop", on_delete=models.CASCADE
    )

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="enemy_drops",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    objects = mixins.SessionManager()


class FriendGift(models.Model):
    game = models.ForeignKey(
        "game.Game", related_name="friend_gifts", on_delete=models.CASCADE
    )
    friend = models.ForeignKey("Friend", related_name="gifts", on_delete=models.CASCADE)
    item = models.ForeignKey(
        "item.Item", related_name="friend_gift", on_delete=models.CASCADE
    )
    dialogue_option = models.ForeignKey(
        "FriendDialogueOption",
        related_name="gifts",
        on_delete=models.CASCADE,
        null=True,
    )

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="friend_drops",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    already_gifted = models.BooleanField(default=False)

    objects = mixins.SessionManager()


class FriendNameChange(models.Model):
    game = models.ForeignKey(
        "game.Game", related_name="friend_name_changes", on_delete=models.CASCADE
    )
    friend = models.ForeignKey(
        "Friend", related_name="name_changes", on_delete=models.CASCADE
    )
    dialogue_option = models.OneToOneField(
        "FriendDialogueOption",
        related_name="name_change",
        on_delete=models.CASCADE,
        null=True,
    )

    new_name = models.CharField(max_length=250)
    new_accepted_names = models.CharField(max_length=1000)
    new_description = models.CharField(max_length=1000)
    new_in_room_description = models.CharField(max_length=1000)

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="friend_name_changes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    already_changed = models.BooleanField(default=False)

    objects = mixins.SessionManager()


class FriendAcceptsItem(models.Model):
    game = models.ForeignKey(
        "game.Game", related_name="friend_items_accepted", on_delete=models.CASCADE
    )
    friend = models.ForeignKey(
        "Friend", related_name="items_accepted", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        "item.Item", related_name="accepted_by_friend", on_delete=models.CASCADE
    )

    hides_dialogue = models.ManyToManyField(
        "FriendDialogueOption", related_name="hidden_by"
    )
    reveals_dialogue = models.ManyToManyField(
        "FriendDialogueOption", related_name="revealed_by"
    )

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="friend_accepts_items",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    received = models.BooleanField(default=False)

    objects = mixins.SessionManager()

    class Meta:
        unique_together = [["friend", "item"]]


class FriendDialogueOption(models.Model):
    friend = models.ForeignKey(
        "Friend", related_name="dialogue_options", on_delete=models.CASCADE
    )
    requires_dialogue = models.ForeignKey(
        "self",
        related_name="sub_options",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    text = models.CharField(max_length=1000)
    talking_point = models.CharField(max_length=250)
    can_back_out = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="friend_dialogue_options",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    already_spoken = models.BooleanField(default=False)

    objects = mixins.SessionManager()

    def get_gift_items(self):
        if self.session is None:
            return self.game.items.base().filter(friend_gift__dialogue_option=self)
        return self.session.items.filter(friend_gift__dialogue_option=self)

    def receive_gifts(self):
        self.get_gift_items().filter(friend_gift__already_gifted=False).update(
            in_inventory=True
        )
        self.gifts.update(already_gifted=True)

    def activate_name_change(self):
        name_change = getattr(self, "name_change", None)
        if name_change is None:
            return

        for field in ["name", "accepted_names", "description", "in_room_description"]:
            new_value = getattr(name_change, f"new_{field}")
            if new_value:
                setattr(self.friend, field, new_value)

            self.friend.save()

    def get_text_display(self):
        if self.session is None:
            return self.text

        return self.text.replace("[PLAYER_NAME]", self.session.player.name)

    def __str__(self):
        return self.text


class ShopkeeperItem(models.Model):
    game = models.ForeignKey(
        "game.Game", related_name="shopkeeper_items", on_delete=models.CASCADE
    )
    shopkeeper = models.ForeignKey(
        "Friend", related_name="store_inventory", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        "item.Item", related_name="sold_by_shopkeeper", on_delete=models.CASCADE
    )
    price = models.PositiveIntegerField()
    currency = models.ForeignKey(
        "game.Currency", related_name="items", on_delete=models.CASCADE
    )

    # session tracking
    session = models.ForeignKey(
        "game.Session",
        related_name="shopkeeper_items",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    sold = models.BooleanField(default=False)

    objects = mixins.SessionManager()
