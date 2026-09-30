#!/usr/bin/env python3
"""
geometry_areas.py - A suite for calculating the area of geometric shapes.

Usage:
    python geometry_areas.py          # interactive menu
    python geometry_areas.py --test   # run built-in self-tests

As a library:
    from geometry_areas import circle, triangle_heron
    circle(5)                  # 78.539...
    triangle_heron(3, 4, 5)    # 6.0
"""

import math
import sys
from typing import Callable, Dict, List, NamedTuple


# --------------------------------------------------------------------------
# Validation helpers
# --------------------------------------------------------------------------
def _positive(**values: float) -> None:
    """Raise ValueError if any value is not a positive finite number."""
    for name, v in values.items():
        if not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
            raise ValueError(f"'{name}' must be a positive number, got {v!r}")


# --------------------------------------------------------------------------
# Area formulas
# --------------------------------------------------------------------------
def square(side: float) -> float:
    """A = s^2"""
    _positive(side=side)
    return side ** 2


def rectangle(length: float, width: float) -> float:
    """A = l * w"""
    _positive(length=length, width=width)
    return length * width


def triangle_base_height(base: float, height: float) -> float:
    """A = (1/2) * b * h"""
    _positive(base=base, height=height)
    return 0.5 * base * height


def triangle_heron(a: float, b: float, c: float) -> float:
    """Heron's formula: A = sqrt(s(s-a)(s-b)(s-c)), s = (a+b+c)/2"""
    _positive(a=a, b=b, c=c)
    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError("Sides violate the triangle inequality")
    s = (a + b + c) / 2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))


def circle(radius: float) -> float:
    """A = pi * r^2"""
    _positive(radius=radius)
    return math.pi * radius ** 2


def semicircle(radius: float) -> float:
    """A = (1/2) * pi * r^2"""
    return circle(radius) / 2


def ellipse(semi_major: float, semi_minor: float) -> float:
    """A = pi * a * b"""
    _positive(semi_major=semi_major, semi_minor=semi_minor)
    return math.pi * semi_major * semi_minor


def circular_sector(radius: float, angle_degrees: float) -> float:
    """A = (theta/360) * pi * r^2, with 0 < theta <= 360"""
    _positive(radius=radius, angle_degrees=angle_degrees)
    if angle_degrees > 360:
        raise ValueError("'angle_degrees' must be <= 360")
    return (angle_degrees / 360) * math.pi * radius ** 2


def annulus(outer_radius: float, inner_radius: float) -> float:
    """A = pi * (R^2 - r^2)"""
    _positive(outer_radius=outer_radius, inner_radius=inner_radius)
    if inner_radius >= outer_radius:
        raise ValueError("Inner radius must be smaller than outer radius")
    return math.pi * (outer_radius ** 2 - inner_radius ** 2)


def parallelogram(base: float, height: float) -> float:
    """A = b * h"""
    _positive(base=base, height=height)
    return base * height


def rhombus(diagonal1: float, diagonal2: float) -> float:
    """A = (d1 * d2) / 2"""
    _positive(diagonal1=diagonal1, diagonal2=diagonal2)
    return diagonal1 * diagonal2 / 2


def trapezoid(base1: float, base2: float, height: float) -> float:
    """A = (1/2) * (a + b) * h"""
    _positive(base1=base1, base2=base2, height=height)
    return 0.5 * (base1 + base2) * height


def kite(diagonal1: float, diagonal2: float) -> float:
    """A = (d1 * d2) / 2"""
    return rhombus(diagonal1, diagonal2)


def regular_polygon(sides: int, side_length: float) -> float:
    """A = n * s^2 / (4 * tan(pi / n)), n >= 3"""
    _positive(side_length=side_length)
    if not isinstance(sides, int) or sides < 3:
        raise ValueError("'sides' must be an integer >= 3")
    return sides * side_length ** 2 / (4 * math.tan(math.pi / sides))


def equilateral_triangle(side: float) -> float:
    """A = (sqrt(3)/4) * s^2"""
    return regular_polygon(3, side)


def hexagon(side: float) -> float:
    """A = (3*sqrt(3)/2) * s^2"""
    return regular_polygon(6, side)


def polygon_shoelace(vertices: List[tuple]) -> float:
    """Shoelace formula for any simple polygon given ordered (x, y) vertices."""
    if len(vertices) < 3:
        raise ValueError("A polygon needs at least 3 vertices")
    total = 0.0
    for i, (x1, y1) in enumerate(vertices):
        x2, y2 = vertices[(i + 1) % len(vertices)]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2


# --------------------------------------------------------------------------
# Registry for the interactive menu
# --------------------------------------------------------------------------
class Shape(NamedTuple):
    name: str
    func: Callable
    params: List[str]
    formula: str


SHAPES: Dict[str, Shape] = {
    "1": Shape("Square", square, ["side"], "A = s²"),
    "2": Shape("Rectangle", rectangle, ["length", "width"], "A = l × w"),
    "3": Shape("Triangle (base & height)", triangle_base_height, ["base", "height"], "A = ½ × b × h"),
    "4": Shape("Triangle (three sides)", triangle_heron, ["a", "b", "c"], "Heron: A = √(s(s-a)(s-b)(s-c))"),
    "5": Shape("Equilateral triangle", equilateral_triangle, ["side"], "A = (√3/4) × s²"),
    "6": Shape("Circle", circle, ["radius"], "A = π r²"),
    "7": Shape("Semicircle", semicircle, ["radius"], "A = ½ π r²"),
    "8": Shape("Ellipse", ellipse, ["semi_major", "semi_minor"], "A = π a b"),
    "9": Shape("Circular sector", circular_sector, ["radius", "angle_degrees"], "A = (θ/360) π r²"),
    "10": Shape("Annulus (ring)", annulus, ["outer_radius", "inner_radius"], "A = π (R² − r²)"),
    "11": Shape("Parallelogram", parallelogram, ["base", "height"], "A = b × h"),
    "12": Shape("Rhombus", rhombus, ["diagonal1", "diagonal2"], "A = d₁ d₂ / 2"),
    "13": Shape("Trapezoid", trapezoid, ["base1", "base2", "height"], "A = ½ (a + b) h"),
    "14": Shape("Kite", kite, ["diagonal1", "diagonal2"], "A = d₁ d₂ / 2"),
    "15": Shape("Regular polygon", regular_polygon, ["sides", "side_length"], "A = n s² / (4 tan(π/n))"),
    "16": Shape("Regular hexagon", hexagon, ["side"], "A = (3√3/2) s²"),
}


# --------------------------------------------------------------------------
# Interactive CLI
# --------------------------------------------------------------------------
def _read_number(prompt: str, as_int: bool = False):
    while True:
        raw = input(f"  {prompt}: ").strip()
        try:
            return int(raw) if as_int else float(raw)
        except ValueError:
            print("  Please enter a valid number.")


def _polygon_cli() -> None:
    print("  Enter vertices in order as 'x y'. Blank line to finish.")
    pts = []
    while True:
        line = input(f"  vertex {len(pts) + 1}: ").strip()
        if not line:
            break
        try:
            x, y = map(float, line.split())
            pts.append((x, y))
        except ValueError:
            print("  Format: two numbers separated by a space.")
    print(f"\n  Area = {polygon_shoelace(pts):.4f}")


def menu() -> None:
    while True:
        print("\n=== Geometric Area Calculator ===")
        for key, s in SHAPES.items():
            print(f"{key:>3}. {s.name}")
        print(" 17. Arbitrary polygon (coordinates)")
        print("  0. Exit")
        choice = input("Select a shape: ").strip()

        if choice == "0":
            print("Goodbye!")
            return
        try:
            if choice == "17":
                _polygon_cli()
                continue
            if choice not in SHAPES:
                print("Invalid choice.")
                continue
            shape = SHAPES[choice]
            print(f"\n{shape.name}  |  {shape.formula}")
            args = [_read_number(p, as_int=(p == "sides")) for p in shape.params]
            print(f"\n  Area = {shape.func(*args):.4f}")
        except ValueError as e:
            print(f"  Error: {e}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            return


# --------------------------------------------------------------------------
# Self-tests
# --------------------------------------------------------------------------
def run_tests() -> None:
    close = lambda a, b: math.isclose(a, b, rel_tol=1e-9)
    checks = [
        close(square(4), 16),
        close(rectangle(3, 5), 15),
        close(triangle_base_height(6, 4), 12),
        close(triangle_heron(3, 4, 5), 6),
        close(equilateral_triangle(2), math.sqrt(3)),
        close(circle(1), math.pi),
        close(semicircle(2), 2 * math.pi),
        close(ellipse(3, 2), 6 * math.pi),
        close(circular_sector(1, 90), math.pi / 4),
        close(annulus(3, 1), 8 * math.pi),
        close(parallelogram(5, 2), 10),
        close(rhombus(6, 8), 24),
        close(trapezoid(3, 5, 4), 16),
        close(kite(6, 4), 12),
        close(regular_polygon(4, 3), 9),
        close(hexagon(1), 3 * math.sqrt(3) / 2),
        close(polygon_shoelace([(0, 0), (4, 0), (4, 3), (0, 3)]), 12),
    ]
    for bad in (lambda: circle(-1), lambda: triangle_heron(1, 2, 10),
                lambda: annulus(1, 2), lambda: regular_polygon(2, 1)):
        try:
            bad()
            checks.append(False)
        except ValueError:
            checks.append(True)
    passed = sum(checks)
    print(f"{passed}/{len(checks)} tests passed")
    sys.exit(0 if passed == len(checks) else 1)


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    else:
        menu()
