
Readme · MD
# Breakout — Power-ups

## Power-up adicional: MoreHealth (Corazón de vida extra)

### Descripción

`MoreHealth` es un power-up de elección propia que le otorga al jugador una
vida adicional. Se representa con el ícono de corazón y cae desde el
ladrillo destruido, igual que el resto de los power-ups del juego.

### Comportamiento

- **Probabilidad de aparición:** al destruir un ladrillo, existe un **20%**
  (`0.2`) de probabilidad de que `MoreHealth` sea generado en la posición
  del ladrillo.
- **Condición de efecto:** al ser recogido por la paleta, el power-up
  revisa cuántas vidas tiene el jugador en ese momento:
  - Si el jugador tiene **menos de 3 vidas**, se le suma **una vida**
    (`play_state.lives += 1`).
  - Si el jugador **ya tiene 3 vidas** (el máximo), el power-up se recoge
    igual, pero **no otorga ninguna vida adicional** — el máximo de vidas
    permitido en el juego es 3.
- En ambos casos, el power-up desaparece de la escena al ser recogido
  (`self.active = False`), sin importar si otorgó una vida o no.
- Al recogerlo, se reproduce un efecto de sonido (`settings.SOUNDS["life"]`).
### Implementación

`MoreHealth` hereda de la clase base `PowerUp` (`src/powerups/PowerUp.py`),
siguiendo el mismo patrón que los demás power-ups del juego (`StickyBall`,
`TwoMoreBall`, `RocketsPower`):

```python
class MoreHealth(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 2)

    def take(self, play_state) -> None:
        play_state.more_health_active = True
        if play_state.lives < 3:
            play_state.lives += 1
        self.active = False
        settings.SOUNDS["life"].play()
```

Se genera de la misma forma que los demás power-ups, a través del
`AbstractFactory` de `src.powerups`, en `PlayState.update`, dentro del
bloque de colisión pelota-ladrillo:

```python
if random.random() < 0.2:
    r = brick.get_collision_rect()
    self.powerups.append(
        self.powerups_abstract_factory.get_factory("MoreHealth").create(
            r.centerx - 8, r.centery - 8
        )
    )
```