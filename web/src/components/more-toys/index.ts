import type { ComponentType } from "react";
import type { ToyProps } from "../toys";
import Abuse from "./abuse";
import Apples from "./apples";
import Gashlycrumb from "./gashlycrumb";
import Howler from "./howler";
import Jump from "./jump";
import Picnic from "./picnic";
import Telephone from "./telephone";
import Friar from "./friar";
import Gematria from "./gematria";
import ITicTacToe from "./itictactoe";
import MadLibs from "./madlibs";
import Password from "./password";
import Rhymer from "./rhymer";
import Scrambler from "./scrambler";
import TwelveDays from "./twelvedays";
import Wod from "./wod";

/**
 * Toys for chapters beyond the first five. Each lives in its own file here and is keyed by
 * the `toy` value in its chapter.json. Add one line per toy.
 */
export const MORE_TOYS: Record<string, ComponentType<ToyProps>> = {
  picnic: Picnic,
  jump: Jump,
  howler: Howler,
  gashlycrumb: Gashlycrumb,
  apples: Apples,
  abuse: Abuse,
  telephone: Telephone,
  twelvedays: TwelveDays,
  rhymer: Rhymer,
  friar: Friar,
  scrambler: Scrambler,
  madlibs: MadLibs,
  gematria: Gematria,
  wod: Wod,
  password: Password,
  itictactoe: ITicTacToe,
};
