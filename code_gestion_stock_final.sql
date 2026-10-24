
CREATE SCHEMA IF NOT EXISTS `gestion_stock`;
USE `gestion_stock` ;

-- -----------------------------------------------------
-- Table `gestion_stock`.`fournisseur`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fournisseur` (
  `idFournisseur` INT NOT NULL AUTO_INCREMENT,
  `NomFournisseur` VARCHAR(100) NOT NULL,
  `AdresseFournisseur` VARCHAR(255) NOT NULL,
  `Tel_Fournisseur` VARCHAR(45) NOT NULL,
  `Email_Fournisseur` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`idFournisseur`)
  );
  
-- -----------------------------------------------------
-- Table `gestion_stock`.`utilisateur`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `utilisateur` (
  `idUtilisateur` INT NOT NULL AUTO_INCREMENT,
  `Nom_Utilisateur` VARCHAR(100) NOT NULL,
  `Poste` VARCHAR(45) NOT NULL,
  `Log_In` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idUtilisateur`),
  UNIQUE INDEX `Log_In_UNIQUE` (`Log_In` ASC) VISIBLE
  );

-- -----------------------------------------------------
-- Table `gestion_stock`.`bon_commande`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bon_commande` (
  `idCommande` INT NOT NULL AUTO_INCREMENT,
  `Date_Commande` DATE NOT NULL,
  `idFournisseur` INT NOT NULL,
  `idUtilisateur` INT NOT NULL,
  PRIMARY KEY (`idCommande`),
  INDEX `idFounisseur_idx` (`idFournisseur` ASC) VISIBLE,
  INDEX `idUtilisateur_idx` (`idUtilisateur` ASC) VISIBLE,
  CONSTRAINT `fk_bon_commande_fournisseur`
    FOREIGN KEY (`idFournisseur`)
    REFERENCES `fournisseur` (`idFournisseur`),
  CONSTRAINT `fk_bon_commande_utilisateur`
    FOREIGN KEY (`idUtilisateur`)
    REFERENCES `utilisateur` (`idUtilisateur`)
    );

-- -----------------------------------------------------
-- Table `gestion_stock`.`categorie`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `categorie` (
  `idCategorie` INT NOT NULL AUTO_INCREMENT,
  `NomCategorie` VARCHAR(45) NOT NULL,
  `Description` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`idCategorie`)
  );

-- -----------------------------------------------------
-- Table `gestion_stock`.`produit`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `produit` (
  `idProduit` INT NOT NULL AUTO_INCREMENT,
  `NomProduit` VARCHAR(100) NOT NULL,
  `Description_produit` TEXT NULL DEFAULT NULL,
  `Prix_Unitaire` DECIMAL(10,2) NOT NULL,
  `Seuil` INT NOT NULL,
  `idCategorie` INT NOT NULL,
  PRIMARY KEY (`idProduit`),
  INDEX `idCategorie_idx` (`idCategorie` ASC) VISIBLE,
  CONSTRAINT `fk_produit_categorie`
    FOREIGN KEY (`idCategorie`)
    REFERENCES `categorie` (`idCategorie`)
    );
-- -----------------------------------------------------
-- Table `gestion_stock`.`ligne_commande`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ligne_commande` (
  `idProduit` INT NOT NULL,
  `idCommande` INT NOT NULL,
  `Quantite_Produit` INT NOT NULL,
  `Prix_Achat` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`idProduit`, `idCommande`),
  INDEX `idCommande_idx` (`idCommande` ASC) VISIBLE,
  CONSTRAINT `fk_ligne_commande_commande`
    FOREIGN KEY (`idCommande`)
    REFERENCES `bon_commande` (`idCommande`),
  CONSTRAINT `fk_ligne_commande_produit`
    FOREIGN KEY (`idProduit`)
    REFERENCES `produit` (`idProduit`)
    );

-- -----------------------------------------------------
-- Table `gestion_stock`.`mouvementstock`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mouvementstock` (
  `idMouvementStock` INT NOT NULL AUTO_INCREMENT,
  `Type_mouvement` ENUM('ENTREE', 'SORTIE') NOT NULL,
  `idProduit` INT NOT NULL,
  `Qte_Produit_Movt` INT NOT NULL,
  `Date_Movt` DATE NOT NULL,
  `idUtilisateur` INT NOT NULL,
  PRIMARY KEY (`idMouvementStock`),
  INDEX `fk_MouvementStock_produit_idx` (`idProduit` ASC) VISIBLE,
  INDEX `fk_MouvementStock_Utilisateur_idx` (`idUtilisateur` ASC) VISIBLE,
  CONSTRAINT `fk_MouvementStock_produit`
    FOREIGN KEY (`idProduit`)
    REFERENCES `produit` (`idProduit`),
  CONSTRAINT `fk_MouvementStock_Utilisateur`
    FOREIGN KEY (`idUtilisateur`)
    REFERENCES `utilisateur` (`idUtilisateur`)
    );

-- -----------------------------------------------------
-- Table `gestion_stock`.`stock`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `stock` (
  `idStock` INT NOT NULL AUTO_INCREMENT,
  `idProduit` INT NOT NULL,
  `Qte_Produit_Dispo` INT NOT NULL CHECK (`Qte_Produit_Dispo` >=0),
  `Emplacement` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idStock`),
  INDEX `idProduit_idx` (`idProduit` ASC) VISIBLE,
  CONSTRAINT `fk_stock_produit`
    FOREIGN KEY (`idProduit`)
    REFERENCES `produit` (`idProduit`)
    );
