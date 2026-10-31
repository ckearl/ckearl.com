const CELL = 12;
const GRAVITY = 1400;
const TERMINAL_VELOCITY = 900;
const MAX_FALLING = 700;
const PILE_SHARE = 0.4;

const CHARS = Array.from({ length: 94 }, (_, index) => String.fromCharCode(33 + index));
const COLORS = ["#2c3a45", "#2c3a45", "#1e2830", "#fbf6ea", "#1f7fcc"];

type Glyph = { char: string; color: string };
type Particle = Glyph & { x: number; y: number; vx: number; vy: number };

const pick = <T,>(items: T[]) => items[Math.floor(Math.random() * items.length)];

// Characters fall as particles, then settle into per-column stacks. Settled
// characters are painted once to an offscreen layer, so a full pile costs the
// same to draw as an empty one.
export class AsciiPile {
  private context: CanvasRenderingContext2D;
  private layer = document.createElement("canvas");
  private layerContext = this.layer.getContext("2d")!;
  private stacks: Glyph[][] = [];
  private particles: Particle[] = [];
  private width = 0;
  private height = 0;
  private scale = 1;
  private maxRows = 0;

  constructor(
    private canvas: HTMLCanvasElement,
    private reduceMotion: boolean,
    private onPileChange: (hasPile: boolean) => void
  ) {
    this.context = canvas.getContext("2d")!;
  }

  get falling() {
    return this.particles.length > 0;
  }

  resize(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.scale = window.devicePixelRatio || 1;
    this.maxRows = Math.floor((height * PILE_SHARE) / CELL);

    const columns = Math.ceil(width / CELL);
    this.stacks = Array.from({ length: columns }, (_, column) =>
      (this.stacks[column] ?? []).slice(0, this.maxRows)
    );

    this.canvas.width = width * this.scale;
    this.canvas.height = height * this.scale;
    this.layer.width = this.canvas.width;
    this.layer.height = this.maxRows * CELL * this.scale;
    for (const context of [this.context, this.layerContext]) {
      context.setTransform(this.scale, 0, 0, this.scale, 0, 0);
      context.font = `${CELL + 2}px ${getComputedStyle(this.canvas).fontFamily}`;
      context.textAlign = "center";
      context.textBaseline = "middle";
    }

    this.stacks.forEach((stack, column) =>
      stack.forEach((glyph, row) => this.paint(glyph, column, row))
    );
    this.draw();
  }

  spawn(x: number, y: number) {
    if (x < 0 || x >= this.width || y < 0 || y >= this.height) return;
    if (this.particles.length >= MAX_FALLING) return;

    const glyph = { char: pick(CHARS), color: pick(COLORS) };
    if (this.reduceMotion) {
      let column = this.columnAt(x);
      let next = this.downhillFrom(column);
      while (next !== null) {
        column = next;
        next = this.downhillFrom(column);
      }
      this.settle(glyph, column);
      this.draw();
      return;
    }

    this.particles.push({
      ...glyph,
      x,
      y,
      vx: (Math.random() - 0.5) * 70,
      vy: Math.random() * 40,
    });
  }

  step(seconds: number) {
    for (let index = this.particles.length - 1; index >= 0; index--) {
      const particle = this.particles[index];
      particle.vy = Math.min(particle.vy + GRAVITY * seconds, TERMINAL_VELOCITY);
      particle.y += particle.vy * seconds;
      particle.x = Math.max(0, Math.min(this.width - 1, particle.x + particle.vx * seconds));

      const column = this.columnAt(particle.x);
      if (particle.y < this.restingY(column)) continue;

      const next = this.downhillFrom(column);
      if (next !== null) {
        particle.x = next * CELL + CELL / 2;
        particle.vx = 0;
        particle.vy *= 0.4;
        continue;
      }

      this.settle(particle, column);
      this.particles[index] = this.particles[this.particles.length - 1];
      this.particles.pop();
    }
  }

  draw() {
    const { context, width, height } = this;
    context.clearRect(0, 0, width, height);
    context.drawImage(
      this.layer,
      0,
      height - this.maxRows * CELL,
      width,
      this.maxRows * CELL
    );
    for (const particle of this.particles) {
      context.fillStyle = particle.color;
      context.fillText(particle.char, particle.x, particle.y + CELL / 2);
    }
  }

  clear() {
    this.particles = [];
    this.stacks = this.stacks.map(() => []);
    this.layerContext.clearRect(0, 0, this.width, this.maxRows * CELL);
    this.draw();
    this.onPileChange(false);
  }

  private columnAt(x: number) {
    return Math.floor(x / CELL);
  }

  private restingY(column: number) {
    return this.height - (this.stacks[column].length + 1) * CELL;
  }

  // Sand behaviour: a character rolls off a ledge two or more rows high.
  private downhillFrom(column: number) {
    const height = this.stacks[column].length;
    const lower = [column - 1, column + 1].filter(
      (neighbor) => neighbor in this.stacks && this.stacks[neighbor].length < height - 1
    );
    return lower.length > 0 ? pick(lower) : null;
  }

  private settle(glyph: Glyph, column: number) {
    const stack = this.stacks[column];
    if (stack.length >= this.maxRows) return;

    const settled = { char: glyph.char, color: glyph.color };
    stack.push(settled);
    this.paint(settled, column, stack.length - 1);
    this.onPileChange(true);
  }

  private paint(glyph: Glyph, column: number, row: number) {
    this.layerContext.fillStyle = glyph.color;
    this.layerContext.fillText(
      glyph.char,
      column * CELL + CELL / 2,
      (this.maxRows - row) * CELL - CELL / 2
    );
  }
}
