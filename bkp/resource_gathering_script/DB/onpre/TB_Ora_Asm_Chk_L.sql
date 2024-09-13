USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Ora_Asm_Chk_L]    Script Date: 2022-02-11 ¿ÀÀü 9:30:03 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Ora_Asm_Chk_L](
	[CollectDT] [varchar](8) NOT NULL,
	[dbName] [varchar](30) NOT NULL,
	[asm_name] [varchar](30) NOT NULL,
	[tot_gb] [decimal](8, 2) NULL,
	[free_gb] [decimal](8, 2) NULL,
	[use_pct] [decimal](5, 2) NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL,
 CONSTRAINT [PK_Ora_Asm_Chk_L] PRIMARY KEY CLUSTERED 
(
	[CollectDT] ASC,
	[dbName] ASC,
	[asm_name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


