# Configuring EFS with ADCS Server 2008
**Posted on June 8, 2012 by mattfeltonma**
Over the past few months I’ve been studying for the 70-640. I decided to put the CCNA on hold since I’m in the process of building a new Server 2008 network. From what I’ve gathered from reviews of the exam from my friends over at Tech Exams, the exam really focuses on AD CS.

In the process of studying for the exam, I’ve been labbing AD CS like crazy. Over the past few days I’ve been setting up a virtual lab similar to the advanced lab detailed in the AD CS Step-by-Step Setup Guide.

Today I decided to play with certificate autoenrollment and EFS. I couldn’t find anything on the web that gave the full details on how to set everything up, so I figured I would write up the process to save others the time it took me to round up all the info.

I’m not going to go into how to setup AD CS, as there are plenty of guides out there that will walk you through the process. With that in mind, let’s begin.

### Step 1: Duplicate the EFS Recover Agent certificate template

First and foremost you’re going to want to setup a recovery agent. You’ll be able to use this account to decrypt any documents that users encrypt with EFS. This can be useful in situations like where you have to restore an encrypted document from a backup or if a user somehow manages to lose his or her private key. Due to the power of this account, you’re going to want to make sure to lock it down.

Open up Server Manager, expand the ADCS role, click on the Certificate Templates node, and right-cick on the EFS Recovery Agent template and select Duplicate Template. Choose the Windows 2008 Enterprise option (the test lab is a pure 2008 network). On the general tab check off the option to publish the certificate to Active Directory. I would recommend this option for most certificate templates. Make sure your Request Handling tab looks like the one pictured below:

#### EFS Recovery Agent - Request Handling tab

Microsoft now recommends you use ECC algorithm rather than the RSA (see Microsoft Changes in EFS). This will require you to change the encryption algorithm on the Cryptography tab from RSA to one of the ECDH variants. Next, tweak your security settings to make sure the accounts you plan on using have the enroll permission. Hit Apply and OK to close the window.

### Step 2: Duplicate the User and Basic EFS certificate templates

You’ll want to do this is the same way you duplicated the template in step 1. The General, Request Handling, and Cryptography tabs are going to have the same settings we discussed above. Make you properly configure your security settings. I would recommend giving users autoenroll on the User certificate. Google will produce a number of guides for configuring autoenroll of certificates.

### Step 3: Add the templates to the issuing CA’s certificate templates

Open up Server Manager on your issuing CA, expand the issuing CA node, right-click the Certificate Templates node and select New -> Certificate Template to Issue. Select the three templates you created and hit OK.

### Step 4: Issue the EFS Recovery Agent certificates

Log on to a computer as the account(s) you want to set as recovery agents, open a new MMC and add the Certificates snap-in, and select the Current User option. Once the snap-in opens, right click over the Personal node, select All Tasks, and Request New Certificate. Select the default policy you are presented with, check off the EFS Recovery Agent template you created, and select Enroll.

At this point you should backup EFS Recovery Agent certificate and private key as detailed in this article. Store the backup in a secure location.

### Step 5: Configure EFS PKI settings in the Default Domain Policy GPO

You’ll now want to configure the GPO that will push your EFS settings out to the clients. I’m going to place the settings directly into the Default Domain Policy.

Open GPMC and navigate to the node listed in the screenshot below. Right-click over the Encrypting File System node and hit Properties. Configure as shown in the screenshots below.

#### EFS GPO - General

On the certificates tab, select the custom Basic EFS template you created.

#### EFS GPO - Certificates

Leave the Cache tab settings as is unless you have a reason to change them. Click Apply and OK to close the window.

Now you’ll need to add the EFS Recovery Agent. Right-click over the Encrypting File System node and select “Add Data Recovery Agent”. Find the accounts you issued the EFS Recovery Agent certificates for and select them.

At this point, you’re done! You have successfully setup the infrastructure for EFS with Server 2008 AD CS. If you autoenrolled the User and Basic EFS certificates, users will be able to encrypt once they reboot their computers. Otherwise, they will need to request them using Web Enrollment or through the Certificates snap-in.

If you end up having to use the EFS Recovery Agent to decrypt an encrypted document, make sure you remember to load the EFS Recovery Agent certificate and private key for the recovery account on the workstation you are logged into. You would accomplish this by exporting the certificate in the same manner as backing up the key. After that, you would open the Certificate snap-in, right-click the Personal node, select Import, and choose the exported certificate.

This was a real learning experience for me and was very useful in reinforcing a number of AD CS concepts. On to Web Enrollment!

### A few additional helpful tips.
- If you receive “parameter is incorrect” when trying to encrypt a document, check the User and Basic EFS certificate templates to make sure you selected an ECC algorithm.
- If you receive “access is denied” when trying to decrypt an encrypted document using an EFS recovery agent account, verify that you have loaded the private key for the EFS recovery agent certificate on the workstation. This error also occurs if you changed the recovery agent certificate and the item was encrypted before the change. You can verify this by checking the thumbprint of the certificate (details tab when you double-click a certificate) against the recovery agent thumbprint of the encrypted document (right-click document -> Advanced button -> Details button).
