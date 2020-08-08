import numpy as np
import os
import hparams as hp
#from utils.files import get_files
from tqdm import tqdm
#from utils.util import remove_outlier
import glob

def get_files(path, extension='.wav') :
    filenames = []
    for filename in glob.iglob(f'{path}/**/*{extension}', recursive=True):
        filenames += [filename]
    return filenames
    
if __name__ == '__main__':
    min_e = []
    min_p = []
    max_e = []
    max_p = []
    nz_min_p = []
    nz_min_e = []

    energy_path = os.path.join(hp.data_dir, 'energy')
    pitch_path = os.path.join(hp.data_dir, 'pitch')
    mel_path = os.path.join(hp.data_dir, 'mels')
    energy_files = get_files(energy_path, extension='.npy')
    pitch_files = get_files(pitch_path, extension='.npy')
    mel_files = get_files(mel_path, extension='.npy')

    assert len(energy_files) == len(pitch_files) == len(mel_files)

    energy_vecs = []
    for f in tqdm(energy_files):
        e = np.load(f)
        #e = remove_outlier(e)
        energy_vecs.append(e)
        min_e.append(e.min())
        nz_min_e.append(e[e>0].min())
        max_e.append(e.max())

    nonzeros = np.concatenate([v[np.where(v != 0.0)[0]] for v in energy_vecs])
    e_mean, e_std = np.mean(nonzeros), np.std(nonzeros)
    print("Non zero Min Energy : {}".format(min(nz_min_e)))
    print("Max Energy : {}".format(max(max_e)))
    print("Energy mean : {}".format(e_mean))
    print("Energy std: {}".format(e_std))



    pitch_vecs = []
    for f in tqdm(pitch_files):
        p = np.load(f)
        #p = remove_outlier(p)
        pitch_vecs.append(p)
        min_p.append(p.min())
        nz_min_p.append(p[p > 0].min())
        max_p.append(p.max())

    nonzeros = np.concatenate([v[np.where(v != 0.0)[0]] for v in pitch_vecs])
    f0_mean, f0_std = np.mean(nonzeros), np.std(nonzeros)
    print("Min Pitch : {}".format(min(min_p)))
    print("Non zero Min Pitch : {}".format(min(nz_min_p)))
    print("Max Pitch : {}".format(max(max_p)))
    print("Pitch mean : {}".format(f0_mean))
    print("Pitch std: {}".format(f0_std))

    np.save(
        os.path.join(hp.data_dir, "e_mean.npy"),
        e_mean.astype(np.float32),
        allow_pickle=False,
    )
    np.save(
        os.path.join(hp.data_dir, "e_std.npy"),
        e_std.astype(np.float32),
        allow_pickle=False,
    )
    np.save(
        os.path.join(hp.data_dir, "f0_mean.npy"),
        f0_mean.astype(np.float32),
        allow_pickle=False,
    )
    np.save(
        os.path.join(hp.data_dir, "f0_std.npy"),
        f0_std.astype(np.float32),
        allow_pickle=False,
    )
    #print("Min Energy : {}".format(min(min_e)))

    #print("Min Pitch : {}".format(min(min_p)))
