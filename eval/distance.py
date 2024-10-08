import argparse
from pathlib import Path
import sys

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.append(str(HERE))
sys.path.append(str(ROOT))

from ChromaCoverId.chroma_features import ChromaFeatures
from ChromaCoverId.cover_similarity_measures import (
    cross_recurrent_plot,
    qmax_measure,
)

from utils import info


def main(args):
    dir_input = Path(args.dir_input)
    covers = list(dir_input.glob("*.wav"))
    covers = sorted(covers)

    if not covers:
        print("No covers found.")
        return

    no_origs = []
    dists = {}
    for cover in covers:
        orig = info.id2path(cover.stem).raw
        if not orig.exists():
            no_origs.append(cover)
            print(f"No original found for {cover.stem}.")
            continue
        dist = get_distance(orig, cover)
        dists[cover.stem] = dist

    if dists:
        write_result(args.path_result, dists, no_origs)


def get_distance(path1, path2):
    chroma1 = ChromaFeatures(str(path1))
    chroma2 = ChromaFeatures(str(path2))
    hpcp1 = chroma1.chroma_hpcp()
    hpcp2 = chroma2.chroma_hpcp()
    crp = cross_recurrent_plot(hpcp1, hpcp2)
    qmax, _ = qmax_measure(crp)
    return qmax


def write_result(path, dists, no_origs):
    sim_avg = sum(dists.values()) / len(dists)
    print(f"Average distance: {sim_avg}")
    with open(path, "w") as f:
        f.write(f"Average distance: {sim_avg}\n\n")
        f.write("Distance per cover:\n")
        for cover, dist in dists.items():
            f.write(f"  {cover}: {dist}\n")
        f.write("\n")
        if no_origs:
            f.write("No original found for covers:\n")
            for cover in no_origs:
                f.write(f"  {cover}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Evaluate cover similarity using qmax measure.")
    parser.add_argument("--dir_input", type=str, default="eval/data/", help="Directory containing cover WAV files. Defaults to 'ROOT/eval/data/'.")
    parser.add_argument("--path_result", type=str, default="eval/qmax.txt", help="Path to save the result. Defaults to 'ROOT/eval/qmax.txt'.")
    args = parser.parse_args()
    main(args)
