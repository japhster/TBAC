def heal_player(player, healing_item):
    if not healing_item.in_inventory:
        return False
    player.current_health = min(
        player.current_health + healing_item.healing, player.health
    )
    player.save()

    healing_item.in_inventory = False
    healing_item.save()

    print(healing_item.in_inventory)

    return True
