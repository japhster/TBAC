def perform_player_attack(session, enemy, attack_pk):
    if attack_pk == 0:
        attack_damage = session.player.base_damage
    else:
        weapon = session.items.get(pk=attack_pk, in_inventory=True)
        attack_damage = weapon.damage

    damage = attack_damage.get_damage()

    enemy.current_health = max(enemy.current_health - damage, 0)
    if enemy.current_health == 0:
        enemy.is_dead = True
        enemy.get_dropped_items().update(room=session.current_location)

    enemy.save()


def perform_enemy_attack(player, enemies):
    for enemy in enemies:
        damage = enemy.damage.get_damage()
        player.current_health = max(player.current_health - damage, 0)
        player.save()
