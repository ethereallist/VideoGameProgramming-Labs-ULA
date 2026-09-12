# Breakout — Power-ups

## Power-up adicional: MoreHealth (Corazón de vida extra)

### Descripción

`MoreHealth` es un power-up de elección propia que le otorga al jugador una
vida adicional. Se representa con el ícono de corazón y cae desde el
ladrillo destruido, igual que el resto de los power-ups del juego.

### Comportamiento

- **Sistema de probabilidad:** el drop de power-ups usa un sistema de dos
  pasos, centralizado en `settings.py`:
  1. Al destruir un ladrillo, se tira una única probabilidad
     `settings.POWERUP_DROP_CHANCE` (actualmente **`0.5`**, 50%) de que
     **algún** power-up caiga en la posición del ladrillo.
  2. Si cae uno, se elige **cuál** de los 4 tipos mediante un sorteo
     ponderado (`random.choices`) usando los pesos relativos definidos en
     `settings.POWERUP_WEIGHTS`:

     | Power-up      | Peso |
     |---------------|------|
     | TwoMoreBall   | 0.35 |
     | StickyBall    | 0.25 |
     | RocketsPower  | 0.25 |
     | MoreHealth    | 0.15 |

  Con estos valores, la probabilidad de que un ladrillo roto específicamente
  largue `MoreHealth` es `0.5 × 0.15 = 0.075` (**7.5%** de los ladrillos).
  Antes cada power-up tiraba su propia probabilidad de forma independiente
  (lo que en la práctica hacía que cayera algún power-up en ~83% de los
  ladrillos); ahora es un único roll + una elección ponderada, así que las
  probabilidades son predecibles y fáciles de ajustar desde `settings.py`
  sin tocar la lógica de `PlayState`.

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