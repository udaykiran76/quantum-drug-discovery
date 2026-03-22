import numpy as np
from rdkit import Chem
from rdkit.Chem import Draw, AllChem, Descriptors
from rdkit.Chem import rdMolDescriptors
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler


def smiles_to_fingerprint(smiles, n_bits=1024):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(f"❌ Invalid SMILES: {smiles}")
        return None
    fingerprint = AllChem.GetMorganFingerprintAsBitVect(
        mol,
        radius=2,
        nBits=n_bits
    )
    return np.array(fingerprint)


def smiles_to_image(smiles, size=(300, 300)):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(f"❌ Invalid SMILES: {smiles}")
        return None
    img = Draw.MolToImage(mol, size=size)
    return img


def reduce_features_pca(X_train, X_test, n_components=8):
    print(f"\nApplying PCA: 1024 → {n_components} features...")
    pca = PCA(n_components=n_components, random_state=42)
    X_train_reduced = pca.fit_transform(X_train)
    X_test_reduced  = pca.transform(X_test)
    variance_kept   = pca.explained_variance_ratio_.sum() * 100
    print(f"✅ PCA complete!")
    print(f"   Original features : 1024")
    print(f"   Reduced features  : {n_components}")
    print(f"   Information kept  : {variance_kept:.1f}%")
    return X_train_reduced, X_test_reduced, pca


def scale_for_quantum(X_train_reduced, X_test_reduced):
    print(f"\nScaling features for quantum circuit...")
    scaler = MinMaxScaler(feature_range=(0, np.pi))
    X_train_scaled = scaler.fit_transform(X_train_reduced)
    X_test_scaled  = scaler.transform(X_test_reduced)
    print(f"✅ Scaling complete!")
    print(f"   Min value : {X_train_scaled.min():.4f}")
    print(f"   Max value : {X_train_scaled.max():.4f}")
    return X_train_scaled, X_test_scaled, scaler


def get_molecule_properties(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return {
        "Molecular Weight"  : round(Descriptors.MolWt(mol), 2),
        "LogP"              : round(Descriptors.MolLogP(mol), 2),
        "H-Bond Donors"     : rdMolDescriptors.CalcNumHBD(mol),
        "H-Bond Acceptors"  : rdMolDescriptors.CalcNumHBA(mol),
        "Rotatable Bonds"   : rdMolDescriptors.CalcNumRotatableBonds(mol),
        "Aromatic Rings"    : rdMolDescriptors.CalcNumAromaticRings(mol),
        "Heavy Atoms"       : mol.GetNumHeavyAtoms(),
        "Ring Count"        : rdMolDescriptors.CalcNumRings(mol),
    }


def check_lipinski(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None, 0
    mw   = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd  = rdMolDescriptors.CalcNumHBD(mol)
    hba  = rdMolDescriptors.CalcNumHBA(mol)
    tpsa = Descriptors.TPSA(mol)
    rb   = rdMolDescriptors.CalcNumRotatableBonds(mol)
    rules = {
        "Molecular Weight < 500 Da" : (mw,   mw < 500,   f"{mw:.1f} Da"),
        "LogP < 5"                  : (logp, logp < 5,   f"{logp:.2f}"),
        "H-Bond Donors <= 5"        : (hbd,  hbd <= 5,   str(hbd)),
        "H-Bond Acceptors <= 10"    : (hba,  hba <= 10,  str(hba)),
        "TPSA < 140"                : (tpsa, tpsa < 140, f"{tpsa:.1f}"),
        "Rotatable Bonds <= 10"     : (rb,   rb <= 10,   str(rb)),
    }
    passed = sum(1 for _, (val, ok, disp) in rules.items() if ok)
    return rules, passed


if __name__ == "__main__":
    print("=" * 50)
    print("Testing features.py")
    print("=" * 50)

    print("\n📌 Test 1: SMILES → Fingerprint")
    smiles = "CC(=O)Oc1ccccc1C(=O)O"
    fp     = smiles_to_fingerprint(smiles)
    print(f"   SMILES    : {smiles}")
    print(f"   FP shape  : {fp.shape}")
    print(f"   FP sample : {fp[:10]}...")

    print("\n📌 Test 2: SMILES → Image")
    img = smiles_to_image(smiles)
    if img:
        img.save("report/aspirin.png")
        print(f"   ✅ Image saved to report/aspirin.png")

    print("\n📌 Test 3: PCA Reduction")
    from data_loader import load_bace_data
    X_train, X_test, y_train, y_test = load_bace_data()
    X_train_r, X_test_r, pca = reduce_features_pca(X_train, X_test)

    print("\n📌 Test 4: Quantum Scaling")
    X_train_s, X_test_s, scaler = scale_for_quantum(X_train_r, X_test_r)

    print("\n📌 Test 5: Molecule Properties")
    props = get_molecule_properties(smiles)
    print(f"   Properties: {props}")

    print("\n📌 Test 6: Lipinski Rules")
    rules, passed = check_lipinski(smiles)
    print(f"   Rules passed: {passed}/6")

    print("\n🎉 features.py working perfectly!")